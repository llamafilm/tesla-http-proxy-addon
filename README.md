# Tesla HTTP Proxy add-on

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fllamafilm%2Ftesla-http-proxy-addon)

## Add-ons

This repository contains the following add-ons

### [Tesla HTTP Proxy](./tesla_http_proxy)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

![Reported Installations][installations-shield-stable]


<!--
Notes to developers after forking or using the github template feature:
- While developing comment out the 'image' key from 'example/config.yaml' to make the supervisor build the addon
  - Remember to put this back when pushing up your changes.
- When you merge to the 'main' branch of your repository a new build will be triggered.
  - Make sure you adjust the 'version' key in 'example/config.yaml' when you do that.
  - Make sure you update 'example/CHANGELOG.md' when you do that.
  - The first time this runs you might need to adjust the image configuration on github container registry to make it public
  - You may also need to adjust the github Actions configuration (Settings > Actions > General > Workflow > Read & Write)
- Adjust the 'image' key in 'example/config.yaml' so it points to your username instead of 'home-assistant'.
  - This is where the build images will be published to.
- Rename the example directory.
  - The 'slug' key in 'example/config.yaml' should match the directory name.
- Adjust all keys/url's that points to 'home-assistant' to now point to your user/fork.
- Share your repository on the forums https://community.home-assistant.io/c/projects/9
- Do awesome stuff!
 -->

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

## Standalone Usage

If you are not running HAOS, the proxy can run separately as a Docker container.  This is also helpful for development while working in the Tesla integration devcontainer.  The included script will start 2 Docker containers, one for Nginx and one for the proxy.  It mimics some HAOS concepts including folder structure and bashio so you can use the same Docker image as the addon.  You may need to modify according to your environemnt.

- Forward https://DOMAIN:443 to localhost:4430
- Start Docker
- Clone this repo
- Navigate to the `standalone` folder
- Copy TLS cert and key to `ssl/fullchain.pem` and `ssl/privkey.pem`
- Set environment variables in `secrets.env`
- Run `start_proxy.sh`
- Start OAuth at http://localhost:8099 and it will callback to https://DOMAIN/callback
- After getting the token, edit `addons.self.options.config.cache` to change true to false and then restart

[installations-shield-stable]: https://img.shields.io/badge/dynamic/json?url=https://analytics.home-assistant.io/addons.json&query=$["c03d64a7_tesla_http_proxy"].total&label=Reported%20Installations&link=https://analytics.home-assistant.io/add-ons
