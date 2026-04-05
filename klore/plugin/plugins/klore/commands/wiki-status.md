---
description: Show compilation state and source counts
allowed-tools: [Bash]
---

# Wiki Status

Run the following command to check knowledge base status:

```bash
source "${CLAUDE_PLUGIN_ROOT}/commands/_check-klore.sh" && klore status
```

If klore is not installed, tell the user to install it with `pipx install klore`.
