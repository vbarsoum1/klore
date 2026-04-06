#!/usr/bin/env bash
# Shared check: ensure Python and klore are available.
# Source this from command scripts: source "$(dirname "$0")/_check-klore.sh"

if ! command -v python3 &>/dev/null; then
  echo "Error: Python 3 is required but not found." >&2
  echo "Install Python 3.10+ from https://python.org" >&2
  exit 1
fi

# Check if klore is available on PATH or in a venv
if command -v klore &>/dev/null; then
  : # klore found on PATH, good to go
elif python3 -c "import klore" &>/dev/null; then
  : # klore importable, use python3 -m klore
  klore() { python3 -m klore "$@"; }
else
  echo "klore is not installed." >&2
  echo "" >&2
  echo "Install with one of:" >&2
  echo "  pipx install klore              (recommended, if pipx is available)" >&2
  echo "  pip install klore               (if no PEP 668 restrictions)" >&2
  echo "  python3 -m venv ~/.klore-venv && ~/.klore-venv/bin/pip install klore" >&2
  echo "    then add ~/.klore-venv/bin to your PATH" >&2
  echo "" >&2
  echo "Or install from source:" >&2
  echo "  pip install /path/to/klore-repo" >&2
  exit 1
fi
