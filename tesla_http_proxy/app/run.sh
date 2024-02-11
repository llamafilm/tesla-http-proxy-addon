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

generate_keypair() {
  # add custom config to Nginx
  printf "\n### Current Nginx configuration ###\n"
  curl -s GET -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/addons/core_nginx_proxy/info | jq .data.options
  
  printf "\n### Adding custom config to /share/nginx_proxy/nginx_tesla.conf ###\n"
  sed "s/__DOMAIN__/${DOMAIN}/g; s/__PROXYHOST__/${HOSTNAME}/g" /app/nginx_tesla.conf > /share/nginx_proxy/nginx_tesla.conf
  cat /share/nginx_proxy/nginx_tesla.conf

  # generate self signed SSL certificate
  printf "\n### Generating self-signed SSL certificate ###\n"
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
  printf "\n### Generating keypair ###\n"
  /root/go/bin/tesla-keygen -f -keyring-debug -keyring-type pass -key-name myself create > /share/tesla/com.tesla.3p.public-key.pem
  cat /share/tesla/com.tesla.3p.public-key.pem
}

# run on first launch only
if ! pass > /dev/null 2>&1; then
  printf "\n### Setting up GnuPG and password-store ###\n"
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
    printf "\n### Found existing keypair ###\n"
  else
    printf "\n### Existing certificate is invalid ###\n"
    generate_keypair
  fi
else
  generate_keypair
fi

if [ -f /data/access_token ]; then
  printf "\n### Found existing customer token ###\n"
  printf "\n### Starting temporary Python app for debugging ###\n"
  python3 /app/run.py
else
  printf "\n### Starting temporary Python app for authorization flow ###\n"
  python3 /app/run.py
fi

printf "\n### Starting Tesla HTTP Proxy ###\n"
/root/go/bin/tesla-http-proxy -keyring-debug -keyring-type pass -key-name myself -cert /data/cert.pem -tls-key /data/key.pem -port 443 -host 0.0.0.0 -verbose
