#!/bin/bash

# see README.md for instructions

set -e

source secrets.env
mkdir -p  nginx
# start nginx container
openssl dhparam -out nginx/dhparams.pem 2048
sed "s/__DOMAIN__/${DOMAIN}/g; s/__PROXYHOST__/tesla_http_proxy/g" ../tesla_http_proxy/rootfs/app/nginx_tesla.conf > nginx/nginx_tesla.conf
echo "Starting nginx container..."
docker rm -f nginx
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
docker rm -f tesla_http_proxy
docker run --rm --name tesla_http_proxy -p 8099:8099 -p 443:443 --network tesla \
    -v ./share:/share \
    -v ./bashio:/tmp/.bashio:ro \
    -e DOMAIN="${DOMAIN}" \
    -e CLIENT_ID="${CLIENT_ID}" \
    -e CLIENT_SECRET="${CLIENT_SECRET}" \
    -e REGION="${REGION}" \
    -e SUPERVISOR_TOKEN="fake-token" \
    ghcr.io/llamafilm/tesla_http_proxy_${ARCH}:1.3.6

