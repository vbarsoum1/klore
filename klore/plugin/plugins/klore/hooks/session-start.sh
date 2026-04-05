#!/usr/bin/env bash
# SessionStart hook — injects wiki context into Claude Code sessions.
# Only runs in directories with a .klore/ config (klore knowledge bases).

[ -d ".klore" ] || exit 0

if [ -f "wiki/index.md" ]; then
  echo "## Klore Knowledge Base"
  echo ""
  echo "A compiled knowledge wiki is available. Use \`/wiki-ask\` to query it."
  echo ""
  cat wiki/index.md
fi
