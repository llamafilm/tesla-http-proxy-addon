#!/usr/bin/with-contenv bashio
set -e

# read options
export CONFIG_PATH=/data/options.json
export CLIENT_ID="$(bashio::config 'client_id')"
export CLIENT_SECRET="$(bashio::config 'client_secret')"
export VIN="$(bashio::config 'vin')"
export DOMAIN="$(bashio::config 'domain')"

export GNUPGHOME=/data/gnugpg
export PASSWORD_STORE_DIR=/data/password-store

if [ -f /share/tesla/com.tesla.3p.public-key.pem ]; then
  printf "\n### Found existing keypair ###\n"
else
  # add custom config to Nginx
  printf "\n### Current Nginx configuration ###\n"
  curl -s GET -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/addons/core_nginx_proxy/info | jq .data.options
  printf "\n### Adding custom config to /share/nginx_proxy/nginx_tesla.conf ###\n"
  sed "s/__DOMAIN__/${DOMAIN}/g" /app/nginx_tesla.conf > /share/nginx_proxy/nginx_tesla.conf

  # generate self signed SSL certificate
  printf "\n### Generating self-signed SSL certificate ###\n"
  openssl req -x509 -nodes -newkey ec \
      -pkeyopt ec_paramgen_curve:secp521r1 \
      -pkeyopt ec_param_enc:named_curve  \
      -subj "/CN=$(hostname)" \
      -keyout /data/key.pem -out /data/cert.pem -sha256 -days 3650 \
      -addext "extendedKeyUsage = serverAuth" \
      -addext "keyUsage = digitalSignature, keyCertSign, keyAgreement"
  mkdir -p /share/tesla
  cp /data/cert.pem /share/tesla/selfsigned.pem

  # setup GnuPG and password-store in persistent data directory
  printf "\n### Generating keypair ###\n"
  mkdir -m 700 -p /data/gnugpg

  gpg --batch --passphrase '' --quick-gen-key myself default default
  gpg --list-keys
  pass init myself

  # Generate keypair.  If key already exists this command will do nothing
  /root/go/bin/tesla-keygen -keyring-debug -keyring-type pass -key-name myself create > /share/tesla/com.tesla.3p.public-key.pem
  cat /share/tesla/com.tesla.3p.public-key.pem
fi

if [ -f /data/access_token ]; then
  printf "\n### Found existing customer token  ###\n"
else
  printf "\n### Starting temporary Python app for authorization flow ###\n"
  python3 /app/run.py
fi

printf "\n### Starting Tesla HTTP Proxy ###\n"
/root/go/bin/tesla-http-proxy -keyring-debug -keyring-type pass -key-name myself -cert /data/cert.pem -tls-key /data/key.pem -port 443 -host 0.0.0.0 -verbose
