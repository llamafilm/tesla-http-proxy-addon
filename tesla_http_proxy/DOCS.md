# Home Assistant Add-on: Tesla HTTP Proxy

## Prerequisites

You must have a domain name (FQDN) with a valid SSL certificate to host your public key on standard port 443. The vehicle will check this key every time you send a command. The easiest way to do this is using [Nginx SSL proxy add-on](https://github.com/home-assistant/addons/tree/master/nginx_proxy). This guide will use `tesla.example.com` as an example.

Configure Nginx to use extra conf files by putting this into the **Customize** field in that addon config:

```yml
active: true
default: nginx_proxy_default*.conf
servers: nginx_proxy/*.conf
```

## How to use

Configure this addon with your domain name, then hit Start. It will initialize and then stop itself after a few seconds. Refresh the page to verify it stopped, then restart the Nginx addon so it loads the new config. Ignore the error: _Failed to restart add-on_.

> [!IMPORTANT]
> At this point your public key should be visible at `https://tesla.example.com/.well-known/appspecific/com.tesla.3p.public-key.pem`, which is required for Tesla's verification process. If this doesn't work, or if it shows any TLS certificate errors, you must fix that before proceeding further.

Request application access at [developer.tesla.com](https://developer.tesla.com). My request was approved immediately but YMMV. This is currently free but it's possible they will monetize it in the future. You will need to provide the following information:

- Name of your legal entity (first and last name is fine)
- App Name, Description, Purpose (can be anything)
- Allow all scopes
- **OAuth Grant Type**: Authorization code and machine-to-machine
- **Allowed Origin**: The FQDN where you are hosting the public key. Must be lowercase, e.g. `https://tesla.example.com`
- **Redirect URI**: Append `/callback` to the FQDN, e.g. `https://tesla.example.com/callback`

Tesla will provide a Client ID and Client Secret. Enter these in addon configuration and then Start it again. Now the `regenerate auth` setting will be automatically disabled.

Use the [Tesla Auth app](https://apps.apple.com/us/app/auth-app-for-tesla/id1552058613) to obtain a refresh token, by entering your Callback URL, Client ID, and Client Secret on the Fleet API page. This will open a webpage that asks for your Tesla account credentials.

> [!TIP]
> The first time you request a refresh token, it will also prompt to authorize your Client ID to access your Tesla account. Allow all scopes.

Using the Home Assistant iOS app, open the Addon Web UI and click **Enroll public key in your vehicle**. This should launch the Tesla app where it prompts for approval to "allow third-party access to your vehicle". If you have multiple vehicles, you'll need to do this on each of them.

> [!NOTE]
> Your Tesla app must already be key-paired with the car.

Configure the [Tesla integration](https://github.com/alandtse/tesla) to use this proxy. It should pre-fill the Client ID, URL, and certificate for you by reading them from this addon.

## Specific setup guides

### Cloudflare

Setting up Tesla HTTP Proxy through cloudflare involves the following steps (all the steps are made with the available addons in home assistant, nothing external. Also it avoids the necessity to open ports on the router):

1. Install **Cloudflared** addon. Then configure like this and start the addon.

```yml
external_hostname: ha.example.com
additional_hosts:
  - hostname: tesla.example.com
    service: https://homeassistant-internal.example.com
```

2. Check on the **Cloudflare dashboard** that the two CNAME DNS Records appeared. If not read the **cloudflared** logs for errors.
   ![image](https://github.com/llamafilm/tesla-http-proxy-addon/assets/1372028/42e637a8-4428-41c7-b244-099aa6844216)
3. Create an `A` type record with name `homeassistant-internal` and IPv4 address pointing to the `LOCAL IP ADDRESS` of the machine hosting the homeassistant instance. Disable `proxied`.
4. Install **Let's Encrypt** addon. (can be done with other addons, check discussions on the repo for alternatives). Then configure like this and make sure to configure the `cloudflare_api_token`. Make sure the `keyfile` and `certfile` aren't already been created. If so, delete them and proceed starting the addon. Read the logs to see when the files are created (takes more than 60 seconds).

```yml
domains:
  - ha.example.com
  - "*.ha.example.com"
  - tesla.example.com
  - homeassistant-internal.example.com
email: null@null.com
keyfile: privkey.pem
certfile: fullchain.pem
challenge: dns
dns:
  provider: dns-cloudflare
  cloudflare_api_token: redacted
```

4. Install **SSL Proxy** addon. (can be done with other addons, check discussions on the repo for alternatives). Then configure like this and make sure the paths to `certfile` and `keyfile` are correct. Start the addon. Make sure no errors appear in the logs.

```yml
domain: homeassistant-internal.example.com
hsts: max-age=31536000; includeSubDomains
certfile: fullchain.pem
keyfile: privkey.pem
cloudflare: true
customize:
  active: true
  default: nginx_proxy_default*.conf
  servers: nginx_proxy/*.conf
```

5. Install **Tesla HTTP Proxy** addon. Configure it as below and then follow all the steps in the `DOCS` making sure to fill the `client_id` and `client_secret`.

```yml
client_id: ""
client_secret: ""
domain: tesla.example.com
debug: false
regenerate_auth: true
region: Europe, Middle East, Africa
```

6. Check on the **Cloudflare dashboard** that in the `SSL/TLS Edge Certificates` there's an active universal certificate for both `example.com` and `*.example.com`. Make sure that in the `SSL/TLS Overview` page the encryption mode is set to `Flexible`

## Troubleshooting

- Check the add-on logs to see what's happening.

- From the add-on Web UI there is a link to test your public key HTTPS endpoint. On iOS this will cause a dialog about "trying to download a configuration profile" because it incorrectly identifies the public key as such.
  If the certificates aren't showing up (most importantly because of some errors) make sure to clear the cache of the browser or just wait some hours.
  On a desktop browser it should display the contents of your public key, similar to this:

```
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEcCTVZI7gyAGiVq2jdBjg4MOiXxsh
nxjvrm2M6uKfDEYS52ITVVbzqGMzzbKCO/tuu78432jU6Z96BNR8NSoRXg==
-----END PUBLIC KEY-----
```

- You should have a config file at `/share/nginx_proxy/nginx_tesla.conf` that hosts the static public key file. You may need to modify this file depending on your SSL config.

- If you get `login_required` error when trying to send API commands, it's likely because you tried to reuse the refresh token more than once. Try fully removing the Tesla integration from HA and adding it back again.

- When you enroll the public key in the vehicle, if you don't get a prompt, try moving within BLE range of the vehicle.

- The refresh token of the fleet-api is relatively short compared to the one for the one used for the old api. Make sure it is similar to this
  `EU_03b5055f7daa4584f95d6169bd1237eaebe1603c2111e5ec3dbb1ea788cf2d21`

- Make sure to read open discussions to see if anyone has similar problems to you.

- Make sure to delete all the old files generated (both for certificates and Tesla HTTP Proxy under shared/tesla) when changing configuration, then rebuild them


## Additional notes

### Tested with

- Tested with a 2021 Model 3 in the United States.
- Tested with a 2023 Model 3 in Europe.
