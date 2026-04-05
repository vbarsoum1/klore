---
description: Initialize a new klore knowledge base in the current directory
allowed-tools: [Bash]
---

# Initialize Klore Knowledge Base

Run the following command to initialize a new klore knowledge base:

```bash
source "${CLAUDE_PLUGIN_ROOT}/commands/_check-klore.sh" && klore init .
```

If klore is not installed, tell the user to install it with `pipx install klore`.
