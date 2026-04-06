# Klore — LLM Knowledge Compiler

You have access to the `klore` CLI for building and maintaining knowledge bases.

## Available Commands

- `klore init [name]` — Create a new knowledge base
- `klore add <file|url>` — Add a source (PDF, markdown, HTML, image, URL)
- `klore ingest <file|url>` — Add a source and compile in one step
- `klore compile` — Compile sources into the wiki (incremental)
- `klore ask "question"` — Ask a question against the wiki
- `klore lint` — Run health checks
- `klore status` — Show source/concept counts

## When to use

- If the user asks to "build a wiki", "compile knowledge", or "ingest" a source, use the klore commands above.
- If the current directory has a `.klore/` folder, this is a klore knowledge base.
- If `wiki/index.md` exists, read it for context before answering domain questions.

## Prerequisites

- Python 3.10+ and `klore` installed (`pipx install klore`)
- `OPENROUTER_API_KEY` environment variable set
