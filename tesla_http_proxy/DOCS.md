# Home Assistant Add-on: Tesla HTTP Proxy

## Prerequisites

You must be running the [Nginx SSL proxy add-on](https://github.com/home-assistant/addons/tree/master/nginx_proxy) because this add-on will add some custom config to that one.

Your Home Assistant must have a domain name (FQDN) with a valid SSL certificate that resolves to a publicly reachable IP address on standard port 443.

You must create an additional DNS record that resolves to the same IP as Home Assistant.  For example, if Home Assistant is `home.example.com` then create `tesla.example.com` as an alias pointing to the same place.

## How to use

Customize the Nginx add-on configuration like this and hit Save

```
active: true
default: nginx_proxy_default*.conf
servers: nginx_proxy/*.conf
```

Configure this addon with your domain name, then hit Start.  It will initialize and then stop itself after a few seconds.  Refresh the page to verify it's stopped, then restart the Nginx addon so it loads the new config. Ignore the error: _Failed to restart add-on_.

At this point your public key should be visible at `https://tesla.example.com/.well-known/appspecific/com.tesla.3p.public-key.pem`, which is required for Tesla's verification process.  If this doesn't work, or if it shows any TLS certificate errors, you must fix that before proceeding further.

Request application access at [developer.tesla.com](https://developer.tesla.com).  My request was approved immediately but YMMV.  This is currently free but it's possible they will monetize it in the future.  You will need to provide the following information:

- Name of your legal entity (first and last name is fine)
- App Name, Description, Purpose (can be anything)
- **Allowed Origin**: matching the FQDN of your Home Assistant server.  Must be lowercase, e.g. `https://tesla.example.com`
- **Redirect URI**: Append `/callback` to the FQDN, e.g. `https://tesla.example.com/callback`
- **Scopes**: `vehicle_device_data`, `vehicle_cmds`, `vehicle_charging_cmds`

Tesla will provide a Client ID and Client Secret.  Enter these in addon configuration and then Start it again.

Using iOS or Android Home Assistant Companion app, navigate to this add-on, select **Web UI** and click **Generate OAuth Token**. This will launch a web browser where you authenticate with Tesla. The API refresh token is printed to the log. Write this down as it will not be shown again after you restart the add-on.
> Note: This was tested on iOS only.  If it doesn't work on Android please open an issue to let us know.

Return to the Companion app addon Web UI and click **Enroll public key in your vehicle**.  This should launch the Tesla app where it prompts for approval.
> Note: Your Tesla app must be key-paired with the car otherwise the public key can't be added.

After that is complete, in the addon Web UI click **Restart this addon**.  Now the Tesla HTTPS proxy should start, and the `Regenerate auth` setting will be automatically disabled.

Configure the [Tesla integration](https://github.com/alandtse/tesla) to use this proxy. It should pre-fill the Client ID and Secret for you by reading them from this addon.

## Troubleshooting

Check the add-on logs to see what's happening.

From the add-on Web UI there is a link to test your public key HTTPS endpoint.  On iOS this will cause a dialog about "trying to download a configuration profile" because it incorrectly identifies the public key as such.  On a desktop browser it should display the contents of your public key, similar to this:

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
