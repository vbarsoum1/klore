---
description: Ask a question against the compiled wiki
argument-hint: <question>
allowed-tools: [Bash]
---

# Ask the Wiki

Run the following command to query the knowledge base:

```bash
source "${CLAUDE_PLUGIN_ROOT}/commands/_check-klore.sh" && klore ask $ARGUMENTS
```

If klore is not installed, tell the user to install it with `pipx install klore`.
