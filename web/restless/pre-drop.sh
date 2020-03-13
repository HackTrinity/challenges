#!/bin/sh
set -e

FLAG="ctf{flag}"
[ -f "/run/secrets/flag.txt" ] && FLAG="$(cat /run/secrets/flag.txt)"
echo "$FLAG" > /flag.txt
chmod o+r /flag.txt
