#!/bin/sh
set -eu
test "$#" -eq 2 || { echo 'Usage: register-agent.sh ROLE MASTER_ORIGIN' >&2; exit 1; }
exec python3 "$(dirname "$0")/join.py" "$1" --master "$2"
