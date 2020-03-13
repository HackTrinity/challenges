#!/bin/sh
set -e

[ -f "/run/secrets/flag.txt" ] && install -o badmin -g badmin -m 660 /run/secrets/flag.txt youwillnevergethisLALALALA.txt

php-fpm7 --daemonize --allow-to-run-as-root
exec nginx -g 'daemon off;'
