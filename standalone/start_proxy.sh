#!/bin/bash

# see DEVELOPERS.md for instructions

#########################################################
# Define these variables in a new file called secrets.env
ARCH=aarch64 # options: aarch64, amd64, armhf, armv7, i386
DEBUG=true # must be lowercase
REGION="North America, Asia-Pacific" # options defined in const.py
DOMAIN=
CLIENT_ID=
CLIENT_SECRET=
#########################################################

set -e
cd "$(dirname "$0")"
source secrets.env
mkdir -p  nginx
# start nginx container
openssl dhparam -dsaparam -out nginx/dhparams.pem 2048
sed "s/__DOMAIN__/${DOMAIN}/g; s/__PROXYHOST__/tesla_http_proxy/g" ../tesla_http_proxy/rootfs/app/nginx_tesla.conf > nginx/nginx_tesla.conf

echo "Making sure we have a clean start if needed ..."
docker rm -f nginx
docker rm -f tesla_http_proxy
docker network rm tesla


echo "Create docker network Tesla...."
docker network create tesla
echo "Starting nginx container..."

docker run --rm --name nginx -d -p 4430:443 -e DOMAIN="$DOMAIN" --network tesla \
    -v ./ssl:/ssl:ro \
    -v ./share:/share:ro \
    -v ./nginx/nginx_tesla.conf:/etc/nginx/conf.d/nginx_tesla.conf:ro \
    -v ./nginx/dhparams.pem:/data/dhparams.pem:ro \
    nginx

## build from source while developing proxy
# git clone https://github.com/llamafilm/tesla-http-proxy-addon.git
# docker build --build-arg BUILD_FROM=ghcr.io/home-assistant/${ARCH}-homeassistant-base tesla-http-proxy-addon/tesla_http_proxy

# start proxy container
# fake token used for Tesla integration CI tests
docker run --rm --name tesla_http_proxy -p 8099:8099 -p 443:443 --network tesla \
    -v ./share:/share \
    -v ./bashio:/tmp/.bashio:ro \
    -e DOMAIN="${DOMAIN}" \
    -e CLIENT_ID="${CLIENT_ID}" \
    -e CLIENT_SECRET="${CLIENT_SECRET}" \
    -e REGION="${REGION}" \
    -e SUPERVISOR_TOKEN="fake-token" \
    -e DEBUG="${DEBUG}" \
    ghcr.io/llamafilm/tesla_http_proxy_"${ARCH}":2.2.7
