#!/bin/sh
set -eu
echo 'Restore is not enabled: needs an encrypted verified backup and operator-held decryption key.' >&2
echo 'No existing files or services were changed.' >&2
exit 2
