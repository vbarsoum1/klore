# Product Requirements Document: LLM Knowledge Base Platform

**Version:** 1.0
 **Date:** April 2, 2026
 **Status:** Draft
 **Origin:** Derived from Andrej Karpathy's public description of his personal LLM-powered knowledge base workflow

------

## 1. Problem Statement

Researchers, engineers, and knowledge workers accumulate vast quantities of heterogeneous source material—papers, articles, repos, datasets, images—across dozens of topics. Today's options for organizing this material fall into two failure modes:

1. **Manual curation tools** (Notion, Obsidian, wikis) require the human to do all the structuring, linking, and maintenance. Quality degrades as volume grows. The knowledge worker becomes a librarian instead of a thinker.
2. **RAG-based Q&A systems** treat the corpus as a retrieval target but produce no persistent, browsable, interlinked knowledge artifact. Answers are ephemeral. Nothing "adds up."

There is no product that treats an LLM as a **compiler** of raw source material into a living, structured, interlinked knowledge base—one that the human can browse, query, lint, and extend—while keeping the raw sources authoritative and the derived wiki regenerable.

------

## 2. Vision

A platform where users drop raw sources into a folder and an LLM **compiles** them into a structured, interlinked markdown wiki—then continuously operates on that wiki to answer questions, generate reports, surface inconsistencies, impute missing data, and suggest new lines of inquiry. The user's every query and exploration feeds back into the wiki, making the knowledge base a compounding asset.

**One-liner:** *Raw sources in, living knowledge base out—maintained by LLMs, navigated by humans.*

------

## 3. Target Users

| Persona                     | Description                                                  | Primary Need                                                 |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Researcher**              | Academic or independent researcher tracking a fast-moving field (AI/ML, biotech, policy) | Synthesize 50–500 sources into navigable, queryable knowledge |
| **Technical Founder / CTO** | Evaluating markets, technologies, competitive landscapes     | Structured competitive/market intelligence that compounds over time |
| **Analyst**                 | Strategy, finance, or intelligence analyst producing reports from diverse source material | Reduce source-to-insight cycle time; maintain audit trail to raw sources |
| **Autodidact**              | Self-directed learner deep-diving a new domain               | Turn a reading list into an interlinked personal curriculum  |

------

## 4. Core Concepts & Terminology

- **Raw Store (`raw/`):** The authoritative source-of-truth directory. User-curated. Contains original articles, papers, images, datasets, code. Never mutated by the LLM.
- **Wiki:** The LLM-compiled derivative. A directory tree of `.md` files with backlinks, concept articles, summaries, index files, and embedded images. Fully regenerable from `raw/`.
- **Compilation:** The process of ingesting a new raw source (or re-processing existing ones) into the wiki—summarizing, categorizing, linking, updating indexes.
- **Filing:** The act of taking a query output (a report, a slide deck, a chart) and incorporating it back into the wiki as a new article or addendum.
- **Linting:** LLM-driven health checks that find inconsistencies, missing data, broken links, stale summaries, and suggest new article candidates or connections.
- **AGENTS.md:** Schema file that describes the wiki's structure, conventions, and rules to the LLM. The LLM's "style guide" for compilation.

------

## 5. Functional Requirements

### 5.1 Data Ingestion

| ID     | Requirement                                                  | Priority |
| ------ | ------------------------------------------------------------ | -------- |
| ING-01 | Accept source documents via drag-and-drop, file picker, or watched folder | P0       |
| ING-02 | Support formats: `.md`, `.txt`, `.pdf`, `.epub`, `.html`, `.csv`, `.json`, `.py`, `.ipynb`, image formats (`.png`, `.jpg`, `.webp`, `.svg`) | P0       |
| ING-03 | Web clipper integration (browser extension) that saves article + images to `raw/` | P0       |
| ING-04 | PDF/EPUB → markdown conversion pipeline (chunked processing for books per Karpathy's epub→txt→chapter-by-chapter approach) | P0       |
| ING-05 | YouTube / podcast transcript ingestion                       | P1       |
| ING-06 | Git repo ingestion (clone, extract README, key source files, structure summary) | P1       |
| ING-07 | Bulk import from existing Obsidian vaults, Notion exports, Roam exports | P1       |
| ING-08 | Image download: given an article, fetch and localize all referenced images | P0       |

### 5.2 Wiki Compilation Engine

| ID     | Requirement                                                  | Priority |
| ------ | ------------------------------------------------------------ | -------- |
| CMP-01 | Incremental compilation: adding one new source should not require reprocessing the entire wiki | P0       |
| CMP-02 | Generate per-source summaries with backlinks to the raw file | P0       |
| CMP-03 | Auto-categorize sources into concept clusters; generate or update concept articles | P0       |
| CMP-04 | Maintain index files: master index, per-category indexes, recently-added index | P0       |
| CMP-05 | Cross-link related concepts, sources, and articles bidirectionally | P0       |
| CMP-06 | Maintain `AGENTS.md` schema file that describes wiki structure and conventions | P0       |
| CMP-07 | Support user-defined compilation rules (e.g., "always extract methodology sections from papers," "tag all sources with date and author") | P1       |
| CMP-08 | Compilation should be idempotent: re-running on the same raw store produces equivalent output | P1       |
| CMP-09 | Provenance tracking: every derived statement links back to the raw source(s) it came from | P0       |

### 5.3 Query & Research Interface

| ID     | Requirement                                                  | Priority |
| ------ | ------------------------------------------------------------ | -------- |
| QRY-01 | Natural language Q&A against the wiki with cited sources     | P0       |
| QRY-02 | Complex multi-hop queries: LLM agent reads multiple articles, synthesizes, and produces a structured answer | P0       |
| QRY-03 | Output formats: markdown article, slide deck (Marp), chart/visualization (matplotlib/plotly → image), structured data (CSV/JSON) | P0       |
| QRY-04 | "File this back" action: one-click to incorporate a query result back into the wiki | P0       |
| QRY-05 | Query history with the ability to replay, refine, or branch  | P1       |
| QRY-06 | CLI interface for programmatic/scripted queries (pipe to other tools, use as LLM tool) | P0       |
| QRY-07 | Web UI for interactive exploration and search                | P0       |
| QRY-08 | The LLM should be able to invoke web search during Q&A to fill gaps | P1       |

### 5.4 Linting & Health Checks

| ID     | Requirement                                                  | Priority |
| ------ | ------------------------------------------------------------ | -------- |
| LNT-01 | Detect inconsistent data across articles (contradictory claims, conflicting numbers) | P0       |
| LNT-02 | Identify missing data and suggest imputation strategies (with web search) | P1       |
| LNT-03 | Surface interesting cross-domain connections for new article candidates | P1       |
| LNT-04 | Detect stale content (raw sources updated but wiki not recompiled) | P0       |
| LNT-05 | Broken link detection (internal wiki links, external URLs)   | P0       |
| LNT-06 | Coverage analysis: which raw sources are under-represented in the wiki? | P1       |
| LNT-07 | Suggest "further questions to ask" based on gaps and patterns | P1       |

### 5.5 Browsing & Visualization

| ID     | Requirement                                                  | Priority |
| ------ | ------------------------------------------------------------ | -------- |
| VIZ-01 | Obsidian-compatible vault structure (user can open the wiki directly in Obsidian) | P0       |
| VIZ-02 | Built-in web-based wiki viewer with graph visualization of concept links | P1       |
| VIZ-03 | Slide deck rendering (Marp) within the viewer                | P1       |
| VIZ-04 | Image and chart rendering inline                             | P0       |
| VIZ-05 | Timeline view for temporally-ordered sources                 | P2       |
| VIZ-06 | Diff view: show what changed in the wiki after a compilation or lint pass | P1       |

### 5.6 Search

| ID     | Requirement                                                  | Priority |
| ------ | ------------------------------------------------------------ | -------- |
| SRC-01 | Full-text search across raw store and wiki                   | P0       |
| SRC-02 | Semantic search (embedding-based similarity)                 | P1       |
| SRC-03 | Faceted filtering: by source type, date range, concept cluster, tag | P1       |
| SRC-04 | Exposable as a CLI tool that LLMs can invoke during queries  | P0       |

------

## 6. Non-Functional Requirements

| Category               | Requirement                                                  |
| ---------------------- | ------------------------------------------------------------ |
| **Scale**              | Must handle wikis up to ~500 sources / ~500K words without degradation. Stretch target: 5,000 sources / 5M words. |
| **Latency**            | Incremental compilation of a single new source: < 60 seconds. Q&A response: < 30 seconds for simple queries, < 120 seconds for multi-hop research queries. |
| **Data Sovereignty**   | All data (raw + wiki) stored locally by default. Cloud sync optional and encrypted. User owns their files—plain `.md` and images on disk, no proprietary format lock-in. |
| **LLM Agnosticism**    | Support pluggable LLM backends: Claude, GPT-4+, Gemini, local models via Ollama/vLLM. Different tasks (ingestion, compilation, Q&A, linting) can use different models. |
| **Offline Capability** | Core browsing and search must work offline. Compilation and Q&A require LLM access (local models enable full offline). |
| **Reproducibility**    | Given the same `raw/` and `AGENTS.md`, compilation should produce semantically equivalent output across runs. |
| **Cost Transparency**  | Track and display token usage per operation (compilation, query, lint). Allow users to set budget caps. |

------

## 7. Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│                     User Interfaces                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Obsidian │  │   Web UI     │  │   CLI / MCP Tool  │  │
│  │  Vault   │  │  (Viewer +   │  │  (Scriptable,     │  │
│  │  View    │  │   Search +   │  │   pipeable,       │  │
│  │          │  │   Q&A)       │  │   LLM-invocable)  │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬──────────┘  │
│       │               │                    │             │
│       └───────────────┼────────────────────┘             │
│                       ▼                                  │
│              ┌─────────────────┐                         │
│              │  Orchestrator   │                         │
│              │  (Task Router)  │                         │
│              └────────┬────────┘                         │
│                       │                                  │
│       ┌───────┬───────┼───────┬──────────┐               │
│       ▼       ▼       ▼       ▼          ▼               │
│  ┌────────┐┌──────┐┌──────┐┌──────┐┌─────────┐          │
│  │Ingest  ││Compile││Query ││ Lint ││ Search  │          │
│  │Pipeline││Engine ││Agent ││Engine││ Index   │          │
│  └───┬────┘└──┬───┘└──┬───┘└──┬───┘└────┬────┘          │
│      │        │       │       │         │                │
│      ▼        ▼       ▼       ▼         ▼                │
│  ┌─────────────────────────────────────────────┐         │
│  │           LLM Router (Model Selection)       │         │
│  │  Fast model → ingestion/extraction           │         │
│  │  Strong model → synthesis/Q&A/linting        │         │
│  └──────────────────────┬──────────────────────┘         │
│                         │                                │
│  ┌──────────────────────┼──────────────────────┐         │
│  │              File System                     │         │
│  │  raw/          wiki/          outputs/       │         │
│  │  (authoritative) (derived)    (reports, etc) │         │
│  └──────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

------

## 8. LLM Model Strategy

Mirrors the two-tier pattern Karpathy implies and that maps well to production cost/quality tradeoffs:

| Task                                                         | Model Tier        | Examples                                              |
| ------------------------------------------------------------ | ----------------- | ----------------------------------------------------- |
| Document reading, extraction, summarization, format conversion | Fast / cheap      | Gemini Flash, Claude Haiku, GPT-4o-mini, local 7B–14B |
| Concept synthesis, cross-linking, Q&A, linting, report generation | Frontier / strong | Claude Opus/Sonnet, GPT-4o, Gemini Pro, local 70B+    |

The system should allow per-task model configuration and expose token cost metrics.

------

## 9. Data Model

```
raw/
├── articles/
│   ├── 2026-04-01_karpathy-llm-kb.md
│   └── 2026-03-28_some-paper.pdf
├── images/
│   └── fig1-architecture.png
├── repos/
│   └── some-repo/
└── datasets/
    └── benchmark-results.csv

wiki/
├── AGENTS.md                  # Schema & conventions
├── INDEX.md                   # Master index
├── concepts/
│   ├── INDEX.md
│   ├── knowledge-compilation.md
│   ├── rag-vs-wiki.md
│   └── incremental-ingestion.md
├── sources/
│   ├── INDEX.md
│   └── karpathy-llm-kb.md    # Summary + backlink to raw/
├── reports/                   # Filed query outputs
│   └── comparison-rag-approaches.md
└── _meta/
    ├── compilation-log.json
    ├── link-graph.json
    └── coverage-report.md
```

------

## 10. Key Workflows

### 10.1 Add New Source

1. User drops file into `raw/` (or uses web clipper / CLI).
2. Ingest pipeline detects new file, converts to processable format.
3. Compile engine reads `AGENTS.md` + existing wiki indexes.
4. LLM generates: source summary, concept tags, updates to relevant concept articles, index updates, new cross-links.
5. Changes written to `wiki/`. Compilation log updated.
6. Search index updated incrementally.

### 10.2 Ask a Question

1. User poses natural language question via UI or CLI.
2. Orchestrator classifies query complexity (simple lookup vs. multi-hop research).
3. Query agent reads relevant wiki indexes, identifies articles to consult.
4. Agent reads articles, optionally invokes search tool, synthesizes answer.
5. Answer rendered in requested format (markdown, slides, chart).
6. User optionally "files" the answer back into `wiki/reports/`.

### 10.3 Lint Pass

1. User triggers lint (or scheduled automatically).
2. Lint engine scans wiki for: inconsistencies, broken links, stale content, coverage gaps.
3. Produces a lint report with specific findings and suggested fixes.
4. User reviews and approves fixes (or sets auto-fix policy for low-risk items like broken links).
5. Approved fixes applied to wiki.

------

## 11. Differentiation from Existing Products

| Product                                   | What It Does                                      | What It Lacks                                                |
| ----------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------ |
| **Obsidian**                              | Excellent `.md` editor and viewer with graph view | No LLM compilation, no auto-linking, no Q&A. The user does all the work. |
| **NotebookLM**                            | LLM-powered Q&A over uploaded docs                | No persistent structured wiki. No incremental compilation. No local-first storage. No CLI. Ephemeral, not compounding. |
| **Perplexity / ChatGPT**                  | Great for one-off research queries                | No persistent knowledge base. No raw source curation. No compounding. |
| **RAG pipelines (LangChain, LlamaIndex)** | Retrieval over document stores                    | Developer toolkits, not products. No wiki output. No browsable artifact. No linting. |
| **Mem.ai / Reflect**                      | AI-assisted note-taking                           | User still writes notes. AI assists but doesn't compile or maintain a structured knowledge artifact. |

The core moat: **the wiki is the artifact.** It's browsable, version-controllable, portable, and it compounds. The LLM is the compiler, not the interface.

------

## 12. Monetization Model (Preliminary)

| Tier                        | Price          | Includes                                                     |
| --------------------------- | -------------- | ------------------------------------------------------------ |
| **Open Core / Self-Hosted** | Free           | CLI + local file system + BYOLLM. Community plugins.         |
| **Pro (Cloud)**             | $25–40/mo      | Hosted web UI, managed LLM calls (with token budget), web clipper, scheduled linting, cloud sync. |
| **Team**                    | $15–25/seat/mo | Shared wikis, access controls, collaborative Q&A, audit trail. |
| **API**                     | Usage-based    | Compilation and Q&A as a service for developers building on top. |

------

## 13. MVP Scope (v0.1)

Ship the tightest loop that proves the core value proposition: **source in → compiled wiki out → queryable.**

| In Scope                              | Out of Scope (v0.2+)                 |
| ------------------------------------- | ------------------------------------ |
| CLI-first interface                   | Web UI                               |
| Markdown, PDF, HTML, image ingestion  | EPUB, video, podcast, repo ingestion |
| Incremental compilation to `.md` wiki | Slide deck / chart output formats    |
| `AGENTS.md` schema management         | User-defined compilation rules       |
| Basic Q&A against wiki                | Multi-hop research agent             |
| Full-text search (CLI)                | Semantic search, faceted filtering   |
| Obsidian-compatible output            | Built-in web viewer                  |
| Single LLM backend (Claude or GPT)    | Multi-model routing                  |
| Manual lint trigger                   | Scheduled linting, auto-fix          |
| Local-only                            | Cloud sync, team features            |

**Target timeline:** 4–6 weeks to functional MVP with a single developer.

------

## 14. Success Metrics

| Metric                                            | Target (MVP)                           | Target (6mo post-launch)   |
| ------------------------------------------------- | -------------------------------------- | -------------------------- |
| Sources → compiled wiki with zero manual editing  | 95% of sources compile cleanly         | 99%                        |
| Q&A accuracy (answer grounded in wiki sources)    | 80% of answers cite correct source     | 90%                        |
| Time to add new source (user effort)              | < 30 seconds (drop file + one command) | < 10 seconds (auto-detect) |
| Wiki "freshness" (% of sources reflected in wiki) | 100% after manual trigger              | 100% continuous            |
| User retention (daily active use)                 | N/A (MVP)                              | 40% WAU/MAU                |
| NPS                                               | N/A (MVP)                              | > 50                       |

------

## 15. Risks & Mitigations

| Risk                                 | Impact                                                       | Mitigation                                                   |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **LLM hallucination in compilation** | Derived wiki contains fabricated claims not in raw sources   | Strict provenance linking (CMP-09). Lint checks cross-reference claims against raw. |
| **Scale ceiling**                    | Context window limits at 500+ articles, 400K+ words          | Auto-maintained indexes and summaries reduce context needed per operation. Chunked processing. Move to embedding-based retrieval at scale. |
| **Cost runaway**                     | Heavy compilation/Q&A burns tokens fast                      | Token budgeting, model tiering (fast model for ingestion, frontier for synthesis), caching of unchanged compilations. |
| **Wiki drift**                       | Repeated incremental compilations accumulate inconsistencies | Periodic full recompilation option. Lint passes. Idempotency tests. |
| **Lock-in perception**               | Users fear dependency on specific LLM provider               | Plain `.md` files on disk. LLM-agnostic design. BYOLLM support. Everything is portable. |
| **Obsidian dependency**              | Obsidian plugin ecosystem changes or declines                | Wiki is just `.md` files—any editor works. Obsidian compatibility is a feature, not a requirement. |

------

## 16. Open Questions

1. **Collaboration model:** Should multiple users be able to contribute to the same `raw/` and share a compiled wiki? What are the merge semantics? NO
2. **Version control:** Should the wiki be automatically git-committed after each compilation? (Likely yes—this is cheap and gives free undo/history.) YES
3. **Selective compilation:** Should users be able to mark certain raw sources as "exclude from wiki" or "include but don't cross-link"? YES
4. **Fine-tuning pathway:** Karpathy mentions synthetic data generation + fine-tuning so the LLM "knows" the data in its weights. Is this a product feature (export training data) or an advanced user workflow? Later. Not now.
5. **Ephemeral wikis:** The "team of LLMs builds a throwaway wiki to answer one hard question" pattern (from Karpathy's Reply 1)—is this a separate product mode or a query-time optimization? query time optimization
6. **Plugin architecture:** Should compilation, linting, and output formatting be extensible via user-defined plugins/scripts? Later not now.