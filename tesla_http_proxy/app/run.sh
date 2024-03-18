#!/command/with-contenv bashio
set -e

# read options
CLIENT_ID="$(bashio::config 'client_id')"; export CLIENT_ID
CLIENT_SECRET="$(bashio::config 'client_secret')"; export CLIENT_SECRET
DOMAIN="$(bashio::config 'domain')"; export DOMAIN
REGION="$(bashio::config 'region')"; export REGION

export GNUPGHOME=/data/gnugpg
export PASSWORD_STORE_DIR=/data/password-store

generate_keypair() {
  # add custom config to Nginx if it's installed
  if ping -c 1 core-nginx-proxy >/dev/null 2>&1; then
    bashio::log.info "Current Nginx configuration"
    bashio::addon.options core_nginx_proxy
    echo

    bashio::log.info "Adding custom config to /share/nginx_proxy/nginx_tesla.conf"
    mkdir -p /share/nginx_proxy
    sed "s/__DOMAIN__/${DOMAIN}/g; s/__PROXYHOST__/${HOSTNAME}/g" /app/nginx_tesla.conf > /share/nginx_proxy/nginx_tesla.conf
    cat /share/nginx_proxy/nginx_tesla.conf
  else
    bashio::log.warning "Nginx is not running"
  fi

  # generate self signed SSL certificate
  bashio::log.info "Generating self-signed SSL certificate"
  openssl req -x509 -nodes -newkey ec \
      -pkeyopt ec_paramgen_curve:secp521r1 \
      -pkeyopt ec_param_enc:named_curve  \
      -subj "/CN=${HOSTNAME}" \
      -keyout /data/key.pem -out /data/cert.pem -sha256 -days 3650 \
      -addext "extendedKeyUsage = serverAuth" \
      -addext "keyUsage = digitalSignature, keyCertSign, keyAgreement"
  mkdir -p /share/tesla
  cp /data/cert.pem /share/tesla/selfsigned.pem

  # Generate keypair
  bashio::log.info "Generating keypair"
  /usr/bin/tesla-keygen -f -keyring-type pass -key-name myself create > /share/tesla/com.tesla.3p.public-key.pem
  cat /share/tesla/com.tesla.3p.public-key.pem
}

# run on first launch only
if ! pass > /dev/null 2>&1; then
  bashio::log.info "Setting up GnuPG and password-store"
  # shellcheck disable=SC2174
  mkdir -m 700 -p /data/gnugpg
  gpg --batch --passphrase '' --quick-gen-key myself default default
  gpg --list-keys
  pass init myself
  generate_keypair

# verify certificate is not from previous install
elif [ -f /share/tesla/com.tesla.3p.public-key.pem ] && [ -f /share/tesla/selfsigned.pem ]; then
  certPubKey="$(openssl x509 -noout -pubkey -in /share/tesla/selfsigned.pem)"
  keyPubKey="$(openssl pkey -pubout -in /data/key.pem)"
  if [ "${certPubKey}" == "${keyPubKey}" ]; then
    bashio::log.info "Found existing keypair"
  else
    bashio::log.warning "Existing certificate is invalid"
    generate_keypair
  fi
else
  generate_keypair
fi

# verify public key is accessible with valid TLS cert
bashio::log.info "Testing public key..."
if ! curl -sfD - "https://$DOMAIN/.well-known/appspecific/com.tesla.3p.public-key.pem"; then
  bashio::log.error "Fix public key before proceeding."
  exit 1
fi

if [ -z "$CLIENT_ID" ]; then
  bashio::log.notice "Request application access with Tesla, then fill in credentials and restart addon."
else
  if bashio::config.true regenerate_auth; then
    bashio::log.notice "Starting temporary Python app for authentication flow"
    python3 /app/run.py
  fi

  bashio::log.info "Starting Tesla HTTP Proxy"
  /usr/bin/tesla-http-proxy -keyring-debug -keyring-type pass -key-name myself -cert /data/cert.pem -tls-key /data/key.pem -port 443 -host 0.0.0.0 -verbose
fi
