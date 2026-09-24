# augmented-llm

A minimal, from-scratch implementation of the **augmented LLM** pattern described in Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents): a single LLM call loop enhanced with **retrieval**, **tools**, and **memory** — the base unit that more complex agent workflows are built from.

No agent framework is used. Every piece (PDF ingestion, chunking, embedding, retrieval, tool dispatch, the agentic loop) is hand-rolled on top of the raw Anthropic and Voyage AI SDKs to make the mechanics explicit.

## What it demonstrates

- **Retrieval (RAG)** — PDFs in `data/` are extracted, chunked, and embedded into an in-memory vector index. A `search_documents` tool lets Claude query that index by cosine similarity.
- **Tools** — Claude can call a sandboxed `calculator` tool (safe AST-based arithmetic, no `eval`) alongside `search_documents`, choosing whichever the query requires — one, both, or neither.
- **Memory** — a single `messages` list is threaded through every turn, so follow-up questions ("going back to my first question...") resolve using prior conversation context.

## Project structure

```
src/augmented_llm/
├── main.py                  # demo entry point: builds the index, runs sample queries
├── config.py                 # pydantic-settings config, loaded from .env
├── models.py                  # DocumentChunk / EmbeddedChunk pydantic models
├── knowledge/
│   ├── extraction.py          # PDF -> raw text (pypdf)
│   ├── chunking.py            # raw text -> sentence-packed DocumentChunks
│   ├── embeddings.py          # DocumentChunks -> EmbeddedChunks (Voyage AI)
│   └── retrieval.py           # cosine-similarity search over embedded chunks
└── agent/
    ├── tools.py                # TOOLS schema, calculator, search tool factory
    └── loop.py                 # run_turn: the tool-use resolution loop
data/                            # source PDFs used to build the demo index
```

## Setup

Requires Python 3.14+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
```

Fill in `.env` with your API keys:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Required. Used for the agent loop. |
| `ANTHROPIC_MODEL` | Optional, defaults to `claude-sonnet-4-5`. |
| `VOYAGE_API_KEY` | Required. Used to embed documents and queries. |
| `VOYAGE_MODEL` | Optional, defaults to `voyage-4`. |

## Usage

```bash
uv run python -m augmented_llm.main
```

This builds an index from `data/prompt engineering.pdf` and runs a fixed set of demo queries that each exercise a different capability: retrieval only, the calculator only, both tools chained together, and a memory-dependent follow-up. Tool calls are printed as they happen, followed by Claude's final answer for each query.

## How it works

1. **`build_index`** extracts text from the PDF, splits it into sentence-complete chunks (~700 chars each), and embeds every chunk with Voyage AI.
2. Each demo query is appended to a shared `messages` list and passed to **`run_turn`**.
3. `run_turn` calls Claude with the full message history and the `TOOLS` schema, then loops: whenever Claude responds with `stop_reason == "tool_use"`, it dispatches to the matching Python function (`calculator` or the closure returned by `make_search_tool`), appends the tool result, and calls Claude again — until Claude returns a plain text answer.
4. Because `messages` accumulates across the whole demo run, later queries can reference earlier ones.
