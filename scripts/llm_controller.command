#!/bin/bash

# Load environment variables from .env file
source "$(dirname "$0")/dot_env_loader.sh"

echo "💻 Scripting from Mac"
source "$VIRTUAL_ENV_PATH"
cd "$REPO_ABSOLUTE_PATH"
# run python script as a module
python -m application.handlers.host_llm "$@"
