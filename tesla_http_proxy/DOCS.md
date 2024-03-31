# Home Assistant Add-on: Tesla HTTP Proxy

## Prerequisites

You must have a domain name (FQDN) with a valid SSL certificate to host your public key on standard port 443.  The vehicle will check this key every time you send a command.
For advanced users, there are many ways to set this up, but this guide assumes Home Assistant is accessible at `https://home.example.com` using [Nginx SSL proxy](https://github.com/home-assistant/addons/blob/master/nginx_proxy/DOCS.md). Add an additional `A` or `CNAME` record for `tesla.example.com` pointing to the same IP address, and an SSL certificate.  You can use [Lets Encrypt](https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md) to make a wildcard certificate that covers both.

Configure Nginx like this:
```yml
domain: home.example.com
hsts: max-age=31536000; includeSubDomains
certfile: fullchain.pem
keyfile: privkey.pem
cloudflare: false
customize:
  active: true
  default: nginx_proxy_default*.conf
  servers: nginx_proxy/*.conf
```

The `home.example.com` domain is not used by this addon so it doesn't matter what you enter there; The next steps will add an additional config file to host the public key at `tesla.example.com`.


## How to use

Configure this addon with your domain name, then hit Start.  It will initialize and then stop itself after a few seconds.  Refresh the page to verify it stopped, then restart the Nginx addon so it loads the new config. Ignore the error: _Failed to restart add-on_.

At this point your public key should be visible at `https://tesla.example.com/.well-known/appspecific/com.tesla.3p.public-key.pem`, which is required for Tesla's verification process.  If this doesn't work, or if it shows any TLS certificate errors, you must fix that before proceeding further.

Request application access at [developer.tesla.com](https://developer.tesla.com).  My request was approved immediately but YMMV.  This is currently free but it's possible they will monetize it in the future.  You will need to provide the following information:

- Name of your legal entity (first and last name is fine)
- App Name, Description, Purpose (can be anything)
- Allow all scopes
- **OAuth Grant Type**: Authorization code and machine-to-machine
- **Allowed Origin**: The FQDN where you are hosting the public key.  Must be lowercase, e.g. `https://tesla.example.com`
- **Redirect URI**: Append `/callback` to the FQDN, e.g. `https://tesla.example.com/callback`

Tesla will provide a Client ID and Client Secret.  Enter these in addon configuration and then Start it again.  Now the `regenerate_auth` setting will be automatically disabled.

Open the Web UI of this addon and click **Login to Tesla account**.  After authenticating, it will redirect to your callback URL which doesn't exist, so you'll see an error like *404 not found*.  That's normal.  Copy the URL from that page and paste it into the text field on the Web UI, then click **Generate token from URL**.  The refresh token will be printed to the log and also copied to your clipboard for later use.

> Tip: The first time you request a refresh token, it will also prompt to authorize your Client ID to access your Tesla account. Allow all scopes.

Using the Home Assistant iOS app, open the Addon Web UI and click **Enroll public key in your vehicle**.  This should launch the Tesla app where it prompts for approval to "allow third-party access to your vehicle".  If you have multiple vehicles, you'll need to do this on each of them. Your Tesla app must already be key-paired with the car.

Configure the [Tesla integration](https://github.com/alandtse/tesla) to use this proxy. It should pre-fill the Client ID, URL, and certificate for you by reading them from this addon.

## Troubleshooting

Enable debug mode and check the add-on logs to see what's happening.

Check the [Wiki](https://github.com/llamafilm/tesla-http-proxy-addon/wiki) for common errors and solutions found by other users.

Feel free to write a new Wiki page if you have been successful at setting this up in a novel way.
