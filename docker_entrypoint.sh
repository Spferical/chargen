#!/bin/sh
USER=chargen
VOLUME=/chargen/data/
chown -R $USER $VOLUME && \
exec gotty -w pipenv --bare run python3 chargen/main.py "$@"
