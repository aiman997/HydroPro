#!/bin/bash

set -e

export DOMAIN="mahrous-amer.com"

if [ -z "$DOMAIN" ]
then
    export DOMAIN="localhost"
fi

caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
