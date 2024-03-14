<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 1.3.2

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
