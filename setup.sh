#!/usr/bin/env bash
# Klore — multi-agent setup script
# Detects installed AI coding agents and configures klore for each one.
set -euo pipefail

KLORE_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIGURED=()

echo "Klore — Multi-Agent Setup"
echo "========================="
echo ""

# ── Check klore CLI ──────────────────────────────────────────────────

if ! command -v klore &>/dev/null; then
  echo "Installing klore CLI..."
  if command -v pipx &>/dev/null; then
    pipx install "$KLORE_DIR"
  elif command -v pip &>/dev/null; then
    pip install "$KLORE_DIR"
  else
    echo "Error: Python pip or pipx required. Install from https://python.org" >&2
    exit 1
  fi
fi

echo "klore CLI: $(command -v klore)"
echo ""

# ── Claude Code ──────────────────────────────────────────────────────

if command -v claude &>/dev/null; then
  echo "Setting up Claude Code..."
  claude plugin marketplace add "$KLORE_DIR/klore/plugin" 2>/dev/null && \
    claude plugin install klore 2>/dev/null && \
    CONFIGURED+=("Claude Code") && \
    echo "  Installed klore plugin with /wiki-* slash commands" || \
    echo "  Plugin already installed"
  CONFIGURED+=("Claude Code")
fi

# ── Cursor ───────────────────────────────────────────────────────────

if [ -d "$HOME/.cursor" ] || command -v cursor &>/dev/null; then
  echo "Setting up Cursor..."
  # Cursor reads rules from .cursor/rules/ in the project
  # The .cursor/rules/klore.mdc file is already in the repo
  CONFIGURED+=("Cursor")
  echo "  Rules file: .cursor/rules/klore.mdc (auto-loaded by Cursor)"
fi

# ── Windsurf ─────────────────────────────────────────────────────────

if [ -d "$HOME/.windsurf" ] || command -v windsurf &>/dev/null; then
  echo "Setting up Windsurf..."
  # Windsurf reads rules from .windsurf/rules/ in the project
  CONFIGURED+=("Windsurf")
  echo "  Rules file: .windsurf/rules/klore.md (auto-loaded by Cascade)"
fi

# ── Codex (OpenAI) ───────────────────────────────────────────────────

if command -v codex &>/dev/null; then
  echo "Setting up Codex..."
  # Codex reads AGENTS.md from the project root
  CONFIGURED+=("Codex")
  echo "  Bootstrap file: AGENTS.md (auto-loaded by Codex)"
fi

# ── GitHub Copilot ───────────────────────────────────────────────────

if command -v gh &>/dev/null && gh extension list 2>/dev/null | grep -q copilot; then
  echo "Setting up GitHub Copilot..."
  CONFIGURED+=("GitHub Copilot")
  echo "  Instructions: .github/copilot-instructions.md"
fi

# ── Summary ──────────────────────────────────────────────────────────

echo ""
echo "========================="
echo "Setup complete!"
echo ""

if [ ${#CONFIGURED[@]} -eq 0 ]; then
  echo "No AI agents detected. Install one of:"
  echo "  - Claude Code:  https://claude.ai/code"
  echo "  - Cursor:       https://cursor.com"
  echo "  - Windsurf:     https://windsurf.com"
  echo "  - Codex:        https://openai.com/codex"
  echo ""
  echo "The klore CLI is still available standalone: klore --help"
else
  echo "Configured for: ${CONFIGURED[*]}"
fi

echo ""
echo "Quick start:"
echo "  klore init my-research"
echo "  cd my-research"
echo "  klore add <file-or-url>"
echo "  klore compile"
echo ""
echo "Don't forget to set your API key:"
echo "  export OPENROUTER_API_KEY=\"sk-or-v1-your-key\""
