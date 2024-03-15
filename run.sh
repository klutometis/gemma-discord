#!/usr/bin/env bash

function main() {
    python3 -m venv venv
    . ./venv/bin/activate
    pip install -r requirements.txt
    ./main
}

# Fail early.
set -e
set -o pipefail

# Start!
main "$@"
