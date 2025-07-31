#!/bin/bash
# List all shell scripts that start the backend (uvicorn, python main.py, or ExecStart with port 8000)

SEARCH_DIR="$(dirname $(dirname "$0"))"

# Find all .sh files and search for backend start commands
find "$SEARCH_DIR" -name "*.sh" | while read -r script; do
  if grep -qE 'uvicorn|python main.py|ExecStart.*8000' "$script"; then
    echo "[STARTUP SCRIPT] $script"
    grep -nE 'uvicorn|python main.py|ExecStart.*8000' "$script"
    echo "---"
  fi
done 