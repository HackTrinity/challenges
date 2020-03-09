#!/bin/sh
set -e

docker-compose build fsbuilder kbuilder
docker-compose run --rm fsbuilder
docker-compose run --rm kbuilder

docker-compose build host
