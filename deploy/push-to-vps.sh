#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 user@host /remote/path"
  exit 1
fi

REMOTE_HOST="$1"
REMOTE_PATH="$2"

rsync -av --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '.env' \
  ./ "${REMOTE_HOST}:${REMOTE_PATH}/"
