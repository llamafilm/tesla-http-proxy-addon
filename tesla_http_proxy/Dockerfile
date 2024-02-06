ARG BUILD_FROM
FROM $BUILD_FROM

# install dependencies
RUN apk add --no-cache \
  python3 \
  py3-flask \
  py3-requests \
  go \
  gpg-agent \
  pass \
  openssl

# install Tesla Go packages
ADD https://github.com/teslamotors/vehicle-command/archive/refs/heads/main.zip /tmp
RUN unzip /tmp/main.zip -d /app
WORKDIR /app/vehicle-command-main
RUN go get ./... && \
  go build ./... && \
  go install ./... 
# installed to /root/go/bin/tesla-http-proxy

# Python 3 HTTP Server serves the current working dir
# So let's set it to our add-on persistent data directory.
WORKDIR /data

# Copy data for add-on
COPY /app /app
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]
