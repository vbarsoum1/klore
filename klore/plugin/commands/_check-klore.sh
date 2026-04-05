#!/usr/bin/env bash
# Shared check: ensure Python and klore are available.
# Source this from command scripts: source "$(dirname "$0")/_check-klore.sh"

if ! command -v python3 &>/dev/null; then
  echo "Error: Python 3 is required but not found." >&2
  echo "Install Python 3.10+ from https://python.org" >&2
  exit 1
fi

if ! python3 -c "import klore" &>/dev/null; then
  echo "klore is not installed. Install with:" >&2
  echo "  pipx install klore    (recommended)" >&2
  echo "  pip install klore     (alternative)" >&2
  exit 1
fi
