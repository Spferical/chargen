#!/bin/sh
USER=chargen
VOLUME=/chargen/data/
chown -R $USER $VOLUME && \
exec gotty -w --title-format "7DRL" pipenv --bare run python3 chargen/main.py "$@"
