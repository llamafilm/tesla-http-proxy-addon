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
