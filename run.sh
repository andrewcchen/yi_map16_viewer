#!/bin/bash -e

cd "$(dirname ${BASH_SOURCE[0]})"

cd src
exec python main.py "$@"
