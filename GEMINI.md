# Klore — LLM Knowledge Compiler

You have access to the `klore` CLI for building and maintaining knowledge bases.

## Available Commands

| Command | What it does |
|---------|-------------|
| `klore init [name]` | Create a new knowledge base |
| `klore add <file\|url>` | Add a source (PDF, markdown, HTML, image, URL) |
| `klore ingest <file\|url>` | Add a source and compile in one step |
| `klore compile` | Compile sources into the wiki (incremental) |
| `klore compile --full` | Force full recompilation |
| `klore ask "question"` | Ask a question against the wiki |
| `klore ask --save "question"` | Ask and save the answer as a wiki report |
| `klore watch` | Watch raw/ for changes and auto-compile |
| `klore lint` | Run health checks (contradictions, broken links) |
| `klore status` | Show source/concept counts, compilation state |

## When to use

- If the user asks to "build a wiki", "compile knowledge", or "ingest" a source, use the klore commands above.
- If the current directory has a `.klore/` folder, this is a klore knowledge base. Check `wiki/index.md` for context.
- If `wiki/index.md` exists, read it to understand what knowledge is available before answering domain questions.

## Prerequisites

- Python 3.10+
- `klore` installed: `pipx install klore` or `pip install klore`
- `OPENROUTER_API_KEY` environment variable set (get one at https://openrouter.ai/keys)
