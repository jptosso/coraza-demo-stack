FROM caddy:2.5.2-builder AS builder

WORKDIR /go/src/github.com/corazawaf
RUN mkdir -p /go/src/github.com/corazawaf && \
    cd /go/src/github.com/corazawaf && \
    git clone --depth 1 https://github.com/corazawaf/coraza-caddy && \    
    cd coraza-caddy && \
    go get ./...
WORKDIR /go/src/github.com/corazawaf/coraza-caddy
RUN go build caddy/main.go && \
    mv main /usr/bin/caddy

FROM caddy:2.5.2

COPY --from=builder /usr/bin/caddy  /usr/bin/caddy
RUN mkdir /coraza && touch /coraza/Caddyfile

WORKDIR /srv
CMD ["/usr/bin/caddy", "run", "--config", "/coraza/Caddyfile", "--adapter", "caddyfile", "--watch"]