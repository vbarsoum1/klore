---
description: Watch raw/ for changes and auto-compile
allowed-tools: [Bash]
---

# Watch Mode

Run the following command to start watching for changes:

```bash
source "${CLAUDE_PLUGIN_ROOT}/commands/_check-klore.sh" && klore watch
```

If klore is not installed, tell the user to install it with `pipx install klore`.
