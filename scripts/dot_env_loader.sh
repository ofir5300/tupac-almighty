#!/bin/bash

# Get the directory of this script, even if called from elsewhere
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
ENV_FILE="$REPO_ROOT/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Missing $ENV_FILE. Aborting."
  exit 1
fi

echo "✅ Loaded $ENV_FILE"
export $(grep -v '^#' "$ENV_FILE" | xargs)