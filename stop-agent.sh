#!/bin/sh
set -eu
test "$(id -u)" -eq 0 || { echo 'Requires operator/root' >&2; exit 1; }
exec systemctl stop agentnet-corner.service
