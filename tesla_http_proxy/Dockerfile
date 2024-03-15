ARG BUILD_FROM
FROM $BUILD_FROM as builder

RUN apk add --no-cache go git

# install Tesla Go packages
RUN git clone https://github.com/teslamotors/vehicle-command.git
WORKDIR /vehicle-command
RUN git checkout 77d5cf3
RUN go get ./... && \
  go build ./... && \
  go install ./...

FROM $BUILD_FROM

COPY --from=builder /root/go/bin/tesla-http-proxy /usr/bin/
COPY --from=builder /root/go/bin/tesla-keygen /usr/bin

# install dependencies
RUN apk add --no-cache \
  python3 \
  py3-flask \
  py3-requests \
  gpg-agent \
  pass \
  openssl

# Python 3 HTTP Server serves the current working dir
WORKDIR /data

# Copy data for add-on
COPY /app /app
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]
