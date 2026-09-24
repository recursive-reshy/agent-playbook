# agent-playbook

Hands-on, from-scratch implementations of every pattern in Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) article.

No agent frameworks (LangChain, LlamaIndex, etc.) — each pattern is built directly on the Anthropic SDK so the underlying mechanics (prompting, control flow, tool dispatch, orchestration) stay visible rather than hidden behind abstractions.

Each pattern lives in its own directory as a self-contained `uv` project.

## Patterns

The article distinguishes **workflows** (predefined code paths orchestrating LLM calls) from **agents** (LLMs dynamically directing their own process), built up from one foundational block.

| # | Pattern | Description | Status |
|---|---|---|---|
| 0 | [augmented-llm](augmented-llm) | The base building block: an LLM enhanced with retrieval, tools, and memory. | ✅ Done |
| 1 | prompt-chaining | Decompose a task into a fixed sequence of LLM calls, each processing the previous step's output. | 🔜 Planned |
| 2 | routing | Classify an input and direct it to a specialized downstream prompt or flow. | 🔜 Planned |
| 3 | parallelization | Run independent subtasks concurrently (sectioning) or the same task multiple times for consensus (voting). | 🔜 Planned |
| 4 | orchestrator-workers | A central LLM dynamically breaks a task into subtasks and delegates them to worker LLMs. | 🔜 Planned |
| 5 | evaluator-optimizer | One LLM generates a response while another evaluates and critiques it in a feedback loop. | 🔜 Planned |
| 6 | autonomous-agent | An open-ended agent that plans, acts, and adapts using tools until a task is complete or a stopping condition is hit. | 🔜 Planned |

## Repo structure

Each directory is an independent `uv`-managed Python project:

```
<pattern-name>/
├── pyproject.toml
├── .env.example
├── src/<package_name>/
└── README.md          # pattern-specific explanation, setup, and usage
```

See each pattern's own README for what it demonstrates and how to run it.

## Setup

Each project manages its own dependencies. From within a pattern's directory:

```bash
uv sync
cp .env.example .env   # fill in required API keys
```

Common keys across projects:

| Variable | Used for |
|---|---|
| `ANTHROPIC_API_KEY` | All LLM calls (Claude). |
| `VOYAGE_API_KEY` | Embeddings, where a pattern uses retrieval. |
