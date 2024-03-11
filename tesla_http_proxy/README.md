# Home Assistant Add-on: Tesla HTTP Proxy

This add-on runs the official [Tesla HTTP Proxy](https://github.com/teslamotors/vehicle-command) to allow Fleet API requests on modern vehicles.  Please do not bother Tesla for support on this.

## About
Runs a temporary Flask web server to handle initial Tesla authorization flow and store the refresh token.  Once that is complete, it quits Flask and runs Tesla's HTTP Proxy code in Go.

Setting this up is fairly complex.  Please read [DOCS.md](https://github.com/llamafilm/tesla-http-proxy-addon/blob/main/tesla_http_proxy/DOCS.md) for details.
