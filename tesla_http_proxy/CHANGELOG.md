<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 2.2.5

### Changed

- Retry public key check if HTTP status code != 200

## 2.2.4

### Changed

- Retry public key check if no IP address is found for the FQDN

## 2.2.3

### Changed

- Use `.cn` endpoints in China
- Nginx returns 404 on `/` location

## 2.2.0

### Added

- Add webpage to generate refresh tokens

### Changed

- Move troubleshooting steps to wiki page

## 2.1.1

### Added

- Add debug config option to control log level

## 2.0.0

### Changed

- Run Web UI as a separate s6-rc service so it's always available
- Simplify nginx config so it no longer needs to access port 8099

### Removed

- Removed OAuth flow because it was too complicated for most users to setup.  Use a separate app to obtain refresh token.

## 1.3.7

### Changed

- Log better error message when "registering Tesla account"

## 1.3.6

### Changed

- Nginx: ignore bad requests without logging
- Remove supervisor dependency, to allow running as standalone Docker container

## 1.3.4

### Changed

- Fail early if public key doesn't work
- Add scopes for energy sites (untested)
- Copy refresh token to clipboard to simplify auth flow

## 1.3.3

### Added

- Support `window_control` with vehicle-command 77d5cf3

### Changed

- Reduce image size by using separate build stage

## 1.3.1

### Changed

- Simplify config flow to avoid 502 error
- Make credentials optional on first launch because Tesla requires public key before approving app request
- Clarify instructions

## 1.2.2

### Changed

- Support all 3 Fleet API regions
- Colored output to help configuration of `tesla_custom` integration

## 1.2.0

### Changed

- Remove unnecessary VIN from config
- Add `regenerate_auth` config option to help with OAuth testing
- Expose ports 443 and 8099 to support external reverse proxies
- Improved error handling when add-on is restarted

## 1.1.0

### Changed

- Skip auth flow if already completed
- Print `refresh_token` to the log
- Correct CN for SSL cert

## 1.0.0

- Initial release
