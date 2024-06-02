### Development

Dev Container can be used for limited testing:

1. Open workspace in VS Code dev container
1. Cmd+Shift+P: Run Task: Start Home Assistant
1. Open web browser on port 7123
1. Run through Home Assitant initialization wizard
1. Enable advanced mode in user settings
1. Cmd+Shift+P: Run Taks: Rebuild Addon

### Testing

To test the proxy, you can make requests from inside the Home Assistant container.  First get the access token, which will expire in a few hours:

```
TESLA_AUTH_TOKEN=$(docker exec -ti addon_c03d64a7_tesla_http_proxy cat access_token)
curl --cacert /share/tesla/selfsigned.pem \
    --header "Authorization: Bearer $TESLA_AUTH_TOKEN" \
    "https://c03d64a7-tesla-http-proxy/api/1/vehicles"
```

### Standalone Usage

While this addon is meant to run in HAOS, it may be useful to run as a standalone Docker container, for CI pipelines or debugging the Tesla integration in a dev container.  This is a work-in-progress script to do that.

Th `start_proxy.sh` script will start 2 Docker containers, one for Nginx and one for the proxy.  It mimics some HAOS concepts including folder structure and bashio so you can use the same Docker image as the addon.  You may need to modify according to your environemnt.

- Forward https://DOMAIN:443 to localhost:4430
- Start Docker
- Clone this repo
- Navigate to the `standalone` folder
- Copy TLS cert and key to `ssl/fullchain.pem` and `ssl/privkey.pem`
- Set environment variables in `secrets.env`
- Run `start_proxy.sh`
- Start OAuth at http://localhost:8099 and follow instructions in [DOCS.md](tesla_http_proxy/DOCS.md).
- After getting the token, edit `addons.self.options.config.cache` to set `regenerate_auth` to false and then restart
