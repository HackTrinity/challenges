#!/bin/sh
set -e

[ -f "/run/secrets/flag.txt" ] || exit 0

cp /run/secrets/flag.txt /
chmod o+r /flag.txt
