#!/command/with-contenv bashio
set -e

# wait for webui.py to avoid interleaved log output
sleep 2

# read options
# you can pass in these variables if running without supervisor
if [ -n "${HASSIO_TOKEN:-}" ]; then
  CLIENT_ID="$(bashio::config 'client_id')"; export CLIENT_ID
  CLIENT_SECRET="$(bashio::config 'client_secret')"; export CLIENT_SECRET
  DOMAIN="$(bashio::config 'domain')"; export DOMAIN
  REGION="$(bashio::config 'region')"; export REGION
  DEBUG="$(bashio::config 'debug')"; export DEBUG
fi

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

# verify domain $DOMAIN has an associated IP address, if not loop and retry
bashio::log.info "Testing $DOMAIN for an associated IP address..."
while :; do
  if ! host $DOMAIN; then
    bashio::log.fatal "$DOMAIN has no associated IP address, add a record in your DNS config."
    bashio::log.fatal "Sleeping 2 minutes before retry."
    sleep 2m
  else
    bashio::log.info "Found an IP address for $DOMAIN"
    break
  fi
done

# verify public key is accessible with valid TLS cert
bashio::log.info "Testing public key..."
set +e
CURL_OUT=$(curl -sfLD - "https://$DOMAIN/.well-known/appspecific/com.tesla.3p.public-key.pem")
set -e
echo "$CURL_OUT"
# last HTTP status code (in case of a redirect)
HTTP_STATUS_CODE=$(echo "$CURL_OUT"|awk '/^HTTP/{print $2}'|tail -1)
while :; do
  if [ "$HTTP_STATUS_CODE" -ne 200 ]; then
    # All good
    bashio::log.info "The public key is accessible."
    break
  else
    bashio::log.fatal "HTTP status code $HTTP_STATUS_CODE; Use a search engine to learn about the status code."
    bashio::log.fatal "If the request keeps failing, adjust your configuration for the request not to fail."
    bashio::log.fatal "Sleeping 2 minutes before retry."
    sleep 2m
  fi
done

if [ -z "$CLIENT_ID" ]; then
  bashio::log.notice "Request application access with Tesla, then fill in credentials and restart addon."
else
  if bashio::config.true regenerate_auth; then
    bashio::log.info "Running auth.py"
    python3 /app/auth.py
  fi

  bashio::log.info "Starting Tesla HTTP Proxy"
  if bashio::config.true debug; then
    /usr/bin/tesla-http-proxy -keyring-debug -keyring-type pass -key-name myself -cert /data/cert.pem -tls-key /data/key.pem -port 443 -host 0.0.0.0 -verbose
  else
    /usr/bin/tesla-http-proxy -keyring-debug -keyring-type pass -key-name myself -cert /data/cert.pem -tls-key /data/key.pem -port 443 -host 0.0.0.0
  fi
fi
