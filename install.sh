#!/usr/bin/env bash
# Klore — one-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/vbarsoum1/llm-wiki-compiler/main/install.sh | bash
set -euo pipefail

echo "Installing Klore — LLM Knowledge Compiler"
echo ""

# ── Install klore via pipx (preferred) or pip ────────────────────────

if command -v pipx &>/dev/null; then
  echo "Installing with pipx..."
  pipx install klore 2>/dev/null || pipx upgrade klore 2>/dev/null || true
elif command -v pip &>/dev/null; then
  echo "Installing with pip..."
  pip install --user klore
else
  echo "Error: Python pip or pipx required."
  echo "Install pipx: python3 -m pip install --user pipx"
  exit 1
fi

# ── Verify ───────────────────────────────────────────────────────────

if command -v klore &>/dev/null; then
  echo ""
  echo "Klore installed successfully!"
  echo "  $(klore --version 2>/dev/null || echo 'klore CLI ready')"
  echo ""
  echo "Quick start:"
  echo "  klore init my-research"
  echo "  cd my-research"
  echo "  klore add <file-or-url>"
  echo "  klore compile"
  echo ""
  echo "Set your API key:"
  echo "  export OPENROUTER_API_KEY=\"sk-or-v1-your-key\""
  echo "  Get one at: https://openrouter.ai/keys"
else
  echo ""
  echo "Warning: klore was installed but is not on PATH."
  echo "Try: python3 -m klore --help"
fi
