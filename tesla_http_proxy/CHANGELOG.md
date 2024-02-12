<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

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
