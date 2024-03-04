# Home Assistant Add-on: Tesla HTTP Proxy

## Prerequisites

You must be running the [Nginx SSL proxy add-on](https://github.com/home-assistant/addons/tree/master/nginx_proxy) because this add-on will add some custom config to that one.

Your Home Assistant must have a domain name (fqdn) with a valid SSL certificate that resolves to a public IP reachable on standard port 443.

For Tesla to reach your server, you must create an additional DNS record that resolves to the public IP of your Home Assistant. For example, if Home Assistant is `home.example.com` then create `tesla.example.com` as an alias pointing to the same place.

## How to use

Request application access at [developer.tesla.com](https://developer.tesla.com).  My request was approved immediately but YMMV.  This is currently free but it's possible they will monetize it in the future.  You will need to provide the following information:

- Name of your legal entity (first and last name is fine)
- App Name, Description, Purpose (can be anything)
- **Allowed Origin**: matching the FQDN of your Home Assistant server.  Must be lowercase, e.g. `https://tesla.example.com`
- **Redirect URI**: Append `/callback` to the FQDN, e.g. `https://tesla.example.com/callback`
- **Scopes**: `vehicle_device_data`, `vehicle_cmds`, `vehicle_charging_cmds`

Tesla will provide a Client ID and Client Secret.  Enter these in add-on configuration.

Customize the Nginx add-on configuration like this and then restart it
```
active: true
default: nginx_proxy_default*.conf
servers: nginx_proxy/*.conf
```

Start this add-on and wait for it to initialize.  It will fail with an error because Nginx is not configured correctly.

Restart this add-on and this time it should succeed.

Using iOS or Android Home Assistant Companion app, navigate to this add-on, select **Web UI** and click **Generate OAuth Token**. This will launch a web browser where you authenticate with Tesla. The API refresh token is printed to the log. Write this down as it will not be shown again after you restart the add-on. Note: For Android, the previous steps should work otherwise please open an issue to let us know.

Return to the Companion app add-on Web UI and click **Enroll public key in your vehicle**. This should launch the Tesla app where it prompts for approval. Note: Your Tesla app must be key-paired with the car otherwise the public key can't be added.

After that is complete, in the Companion app click **Shutdown Flask Server**.  The Flash server shutdown causes the app to display "add-on seems to not be ready", this is expected.  The Tesla HTTPS proxy has restarted, and the `Regenerate auth` setting will be automatically disabled.

Configure the [Tesla integration](https://github.com/alandtse/tesla) to use this proxy.

## Troubleshooting

Check the add-on logs to see what's happening.

From the add-on Web UI there is a link to test your public key HTTPS endpoint.  It should return the contents of your public key, similar to this:

```
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEcCTVZI7gyAGiVq2jdBjg4MOiXxsh
nxjvrm2M6uKfDEYS52ITVVbzqGMzzbKCO/tuu78432jU6Z96BNR8NSoRXg==
-----END PUBLIC KEY-----
```

You should have a config file at `/share/nginx_proxy/nginx_tesla.conf` that does two things.  You may need to modify this file depending on your SSL config.

- Host the static public key file
- Proxy port 8099 to the built in Flask app

This was tested with a 2021 Model 3 in the United States.  Other regions may require different endpoints.

If you get `login_required` error when trying to send API commands, it's likely because you tried to reuse the refresh token more than once.  https://github.com/teslamotors/vehicle-command/issues/160

To test the proxy, you can make requests from inside the Home Assistant container like this: 

```
curl --cacert /share/tesla/selfsigned.pem \
    --header "Authorization: Bearer $TESLA_AUTH_TOKEN" \
    "https://addon-tesla-http-proxy/api/1/vehicles"
```
