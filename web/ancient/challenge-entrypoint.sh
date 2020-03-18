#!/bin/sh
set -e

php-fpm7 --daemonize --allow-to-run-as-root
exec nginx -g 'daemon off;'
