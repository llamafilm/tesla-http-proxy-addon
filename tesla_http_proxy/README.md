# Home Assistant Add-on: Tesla HTTP Proxy

This add-on runs the official [Tesla HTTP Proxy](https://github.com/teslamotors/vehicle-command) to allow Fleet API requests on modern vehicles.

## About
Runs a temporary Flask web server to handle initial Tesla authorization flow and store the refresh token.  Once that is complete, it quits Flask and runs Tesla's HTTP Proxy code in Go.

Setting this up is fairly complex.  Please read [DOCS.md](./DOCS.md) for details.
