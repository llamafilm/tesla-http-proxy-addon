# Home Assistant Add-on: Tesla HTTP Proxy

## Prerequisites

You must have a domain name (FQDN) with a valid SSL certificate to host your public key on standard port 443.  The vehicle will check this key every time you send a command.  The easiest way to do this is using [Nginx SSL proxy add-on](https://github.com/home-assistant/addons/tree/master/nginx_proxy).  This guide will use `tesla.example.com` as an example.
If you're already using your domain name to host Home Asisstant, you'll need to create a new CNAME record for `tesla.example.com` that points to it, and an SSL certificate for both.  I recommend making a wildcard certificate using Lets Encrypt.

Configure Nginx to use extra conf files by putting this into the **Customize** field in that addon config:

```yml
active: true
default: nginx_proxy_default*.conf
servers: nginx_proxy/*.conf
```

## How to use

Configure this addon with your domain name, then hit Start.  It will initialize and then stop itself after a few seconds.  Refresh the page to verify it stopped, then restart the Nginx addon so it loads the new config. Ignore the error: _Failed to restart add-on_.

> [!IMPORTANT]
> At this point your public key should be visible at `https://tesla.example.com/.well-known/appspecific/com.tesla.3p.public-key.pem`, which is required for Tesla's verification process.  If this doesn't work, or if it shows any TLS certificate errors, you must fix that before proceeding further.

Request application access at [developer.tesla.com](https://developer.tesla.com).  My request was approved immediately but YMMV.  This is currently free but it's possible they will monetize it in the future.  You will need to provide the following information:

- Name of your legal entity (first and last name is fine)
- App Name, Description, Purpose (can be anything)
- Allow all scopes
- **OAuth Grant Type**: Authorization code and machine-to-machine
- **Allowed Origin**: The FQDN where you are hosting the public key.  Must be lowercase, e.g. `https://tesla.example.com`
- **Redirect URI**: Append `/callback` to the FQDN, e.g. `https://tesla.example.com/callback`

Tesla will provide a Client ID and Client Secret.  Enter these in addon configuration and then Start it again.  Now the `regenerate auth` setting will be automatically disabled.

Use the [Tesla Auth app](https://apps.apple.com/us/app/auth-app-for-tesla/id1552058613) to obtain a refresh token, by entering your Callback URL, Client ID, and Client Secret on the Fleet API page. This will open a webpage that asks for your Tesla account credentials.

> [!TIP]
> The first time you request a refresh token, it will also prompt to authorize your Client ID to access your Tesla account. Allow all scopes.

Using the Home Assistant iOS app, open the Addon Web UI and click **Enroll public key in your vehicle**.  This should launch the Tesla app where it prompts for approval to "allow third-party access to your vehicle".  If you have multiple vehicles, you'll need to do this on each of them.
> [!NOTE]
> Your Tesla app must already be key-paired with the car.

Configure the [Tesla integration](https://github.com/alandtse/tesla) to use this proxy. It should pre-fill the Client ID, URL, and certificate for you by reading them from this addon.

## Troubleshooting

Check the add-on logs to see what's happening.

From the add-on Web UI there is a link to test your public key HTTPS endpoint.  On iOS this will cause a dialog about "trying to download a configuration profile" because it incorrectly identifies the public key as such.  On a desktop browser it should display the contents of your public key, similar to this:

```
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEcCTVZI7gyAGiVq2jdBjg4MOiXxsh
nxjvrm2M6uKfDEYS52ITVVbzqGMzzbKCO/tuu78432jU6Z96BNR8NSoRXg==
-----END PUBLIC KEY-----
```

You should have a config file at `/share/nginx_proxy/nginx_tesla.conf` that hosts the static public key file.  You may need to modify this file depending on your SSL config.  

This was tested with a 2021 Model 3 in the United States.  Other regions may require different endpoints.

If you get `login_required` error when trying to send API commands, it's likely because you tried to reuse the refresh token more than once.  Try fully removing the Tesla integration from HA and adding it back again.

When you enroll the public key in the vehicle, if you don't get a prompt, try moving within BLE range of the vehicle.
