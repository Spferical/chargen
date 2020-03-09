#!/bin/sh
USER=chargen
chown -R $USER /chargen && su - chargen -c \
'cd /chargen && gotty -w --title-format "Game of Centuries" pipenv --bare run python3 chargen/main.py'
