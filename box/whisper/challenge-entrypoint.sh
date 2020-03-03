#!/bin/sh
set -e

FLAG="flag{test}"
[ -f "/run/secrets/flag.txt" ] && FLAG="$(cat /run/secrets/flag.txt)"

gcc -DFLAG="\"$FLAG\"" -o /usr/local/bin/whisper /opt/whisper.c
rm /opt/whisper.c
chmod u=x,g=x,o=x /usr/local/bin/whisper

exec dropbear -RFEwB -G whisper
