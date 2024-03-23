# Home Assistant Add-on: Tesla HTTP Proxy

This add-on runs the official [Tesla HTTP Proxy](https://github.com/teslamotors/vehicle-command) to allow Fleet API requests on modern vehicles.  Please do not bother Tesla for support on this.

## About
Runs through the Fleet API authorization procedure and then runs Tesla's HTTP Proxy code in Go.  Also runs a simple web server that allows you to enroll your public key in your vehicle.

Setting this up is fairly complex.  Please read [DOCS.md](https://github.com/llamafilm/tesla-http-proxy-addon/blob/main/tesla_http_proxy/DOCS.md) for details.  If you need help, you can try starting a discussion on GitHub.  Please do not open an issue unless you've found a bug.
