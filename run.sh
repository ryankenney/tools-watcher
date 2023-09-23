#!/bin/bash

# Fail on any error or undefined variable
set -e -o pipefail -u

SCRIPT_FILE="$(basename "$0")"
# NOTE: readlink will not work in OSX, but this more complex command is more universal
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$SCRIPT_DIR"
bash container.sh run --rm -it -p 127.0.0.1:5000:5000 --device=/dev/video0:/dev/video0 --name tools-watcher tools-watcher:local-build
