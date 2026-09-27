# prompt-chaining

A minimal, from-scratch implementation of the **prompt chaining** workflow described in Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents): a task is decomposed into a fixed sequence of LLM calls, where each step processes the output of the previous one, with programmatic **gates** in between to check that the chain is still on track.

No agent framework is used. The chain is plain Python control flow over the raw Anthropic SDK, so every step, hand-off, and check is visible.

## What it demonstrates

The example task is writing a blog post from a topic, split into three LLM calls:

```
topic ──▶ [1. outline] ──▶ gate ──▶ [2. draft] ──▶ [3. polish] ──▶ final post
               ▲             │
               └─ feedback ──┘  (retry on failure, up to 3 attempts)
```

- **Decomposition**: each step has a narrow job with its own system prompt (editor → writer → copy editor). Smaller, focused calls are easier to get right than one large prompt.
- **Structured hand-off**: step 1 returns a typed `Outline` (via forced tool use and Pydantic validation) instead of free text, so the next step and the gate can work with real data.
- **Gate**: `check_outline` is plain code, not an LLM call. It checks the outline's shape: non-empty title, 3–6 sections, no duplicate headings, 2–4 key points per section.
- **Feedback loop on failure**: if the gate fails, its issues go back into the outline prompt and step 1 is retried. After 3 failed attempts the chain stops with a `GateFailedError` rather than passing bad input downstream.

## Project structure

```
src/prompt_chaining/
├── cli.py        # argparse entry point (`prompt-chaining` script)
├── chain.py      # run_chain / build_outline: step order, gate, retry loop
├── steps.py      # the three LLM steps: generate_outline, write_draft, polish
├── gates.py      # check_outline: programmatic validation between steps
├── llm.py        # complete_text / complete_structured wrappers over the Anthropic SDK
├── models.py     # Outline, OutlineSection, BlogPost pydantic models
└── config.py     # pydantic-settings config, loaded from .env
```

## Setup

Requires Python 3.14+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
```

Fill in `.env`:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Required. Used for every step in the chain. |
| `MODEL` | Optional, defaults to `claude-sonnet-5`. |
| `MAX_TOKENS` | Optional, defaults to `4096`. |

`.env` is read from the current working directory, so run commands from this directory.

## Usage

```bash
# Print the final post to stdout
uv run prompt-chaining "Why vector databases matter for RAG"

# Save the final post to a file
uv run prompt-chaining "Why vector databases matter for RAG" -o post.md
```

Progress is logged as each step runs (outline attempts, gate result, draft, polish). If the outline never passes the gate, the gate's issues are logged and the command exits with status 1.

## How it works

1. **`generate_outline`** asks Claude for an outline and forces a `submit_output` tool call whose input schema is `Outline.model_json_schema()`. The tool input is validated into an `Outline`.
2. **`check_outline`** validates the outline. If it fails, **`build_outline`** calls `generate_outline` again with the list of issues added to the prompt, up to `max_attempts` (3).
3. **`write_draft`** renders the outline as markdown and asks Claude to write the full post following it exactly.
4. **`polish`** passes the draft to a copy-editing prompt that tightens the prose without changing the structure.
5. **`run_chain`** returns a `BlogPost` with the topic, outline, draft, and final text. The CLI prints or saves `final`.
