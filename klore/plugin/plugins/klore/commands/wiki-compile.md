---
description: Compile raw sources into the wiki (incremental by default)
argument-hint: "[--full] [--topic TOPIC]"
allowed-tools: [Bash]
---

# Compile Wiki

Run the following command to compile the knowledge base:

```bash
source "${CLAUDE_PLUGIN_ROOT}/commands/_check-klore.sh" && klore compile $ARGUMENTS
```

If klore is not installed, tell the user to install it with `pipx install klore`.
