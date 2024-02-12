#!/usr/bin/with-contenv bashio
set -e

# read options
export CLIENT_ID="$(bashio::config 'client_id')"
export CLIENT_SECRET="$(bashio::config 'client_secret')"
export DOMAIN="$(bashio::config 'domain')"

export GNUPGHOME=/data/gnugpg
export PASSWORD_STORE_DIR=/data/password-store

generate_keypair() {
  # add custom config to Nginx if it's installed
  if ping -c 1 core-nginx-proxy >/dev/null 2>&1; then
    bashio::log.info "Current Nginx configuration"
    bashio::addon.options core_nginx_proxy
    #curl -s GET -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/addons/core_nginx_proxy/info | jq .data.options
    
    bashio::log.info "Adding custom config to /share/nginx_proxy/nginx_tesla.conf"
    mkdir -p /share/nginx_proxy
    sed "s/__DOMAIN__/${DOMAIN}/g; s/__PROXYHOST__/${HOSTNAME}/g" /app/nginx_tesla.conf > /share/nginx_proxy/nginx_tesla.conf
    cat /share/nginx_proxy/nginx_tesla.conf
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
  /root/go/bin/tesla-keygen -f -keyring-type pass -key-name myself create > /share/tesla/com.tesla.3p.public-key.pem
  cat /share/tesla/com.tesla.3p.public-key.pem
}

# run on first launch only
if ! pass > /dev/null 2>&1; then
  bashio::log.info "Setting up GnuPG and password-store"
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

if [ -f /data/access_token ] || bashio::config.true regenerate_auth; then  
  bashio::log.notice "Starting temporary Python app for authentication flow"
  python3 /app/run.py
  # disable this setting so the proxy launches immediately next time
  bashio::addon.option regenerate_auth false
fi

bashio::log.info "Starting Tesla HTTP Proxy"
/root/go/bin/tesla-http-proxy -keyring-debug -keyring-type pass -key-name myself -cert /data/cert.pem -tls-key /data/key.pem -port 443 -host 0.0.0.0 -verbose
