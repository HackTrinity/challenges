#!/bin/sh
set -e

install -o nobody -g nogroup -d /run/nginx

[ -f "/run/secrets/flag.txt" ] || exit 0

cp /run/secrets/flag.txt /opt/html/
chmod o+r /opt/html/flag.txt
