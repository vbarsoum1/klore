---
description: Add a source file or URL and compile in one step
argument-hint: <file-or-url>
allowed-tools: [Bash]
---

# Ingest Source

Run the following command to add a source and compile:

```bash
source "${CLAUDE_PLUGIN_ROOT}/commands/_check-klore.sh" && klore ingest $ARGUMENTS
```

If klore is not installed, tell the user to install it with `pipx install klore`.
