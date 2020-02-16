#!/bin/sh

[ -z "$FLAG" ] && FLAG="$(cat /flag.txt)"
sqlite3 CTFd/ctfd.db "UPDATE flags SET content = '$FLAG' WHERE id = 1;"

exec gunicorn 'CTFd:create_app()' \
    --bind '0.0.0.0:80' \
    --workers 1 \
    --worker-tmp-dir "/dev/shm" \
    --worker-class "gevent"
