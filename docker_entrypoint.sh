#!/bin/sh
USER=chargen
chown -R $USER /chargen && su - chargen -c \
'cd /chargen && gotty -w --title-format 7DRL pipenv --bare run python3 chargen/main.py'
