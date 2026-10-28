#!/usr/bin/env sh
# Install requirements-dev.txt first; use PYTHON to select an environment.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"${PYTHON:-python3}" -m build --no-isolation "$@"
