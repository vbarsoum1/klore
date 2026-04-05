---
description: Run health checks on the compiled wiki
allowed-tools: [Bash]
---

# Lint Wiki

Run the following command to check wiki health:

```bash
source "${CLAUDE_PLUGIN_ROOT}/commands/_check-klore.sh" && klore lint
```

If klore is not installed, tell the user to install it with `pipx install klore`.
