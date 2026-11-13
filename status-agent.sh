#!/bin/sh
set -eu
exec systemctl status agentnet-corner.service --no-pager
