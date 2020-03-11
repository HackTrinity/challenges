#!/bin/sh
set -e

docker-compose build fsbuilder kbuilder
docker-compose run --rm fsbuilder
docker-compose run --rm kbuilder

docker-compose build host

wine pyinstaller --workpath pyinstaller_build/ --specpath pyinstaller_build/ --distpath . --onefile --windowed --icon "$(pwd)/pf_senseless.ico" gui_firmtool.pyw
