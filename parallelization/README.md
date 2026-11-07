# Parallelization

An implementation of the **parallelization** pattern from Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). The demo is a code reviewer that uses both variants of the pattern: **sectioning** and **voting**.

## The pattern

Parallelization means running several LLM calls at the same time and combining the results with code. Your code decides the split up front, which is what separates it from orchestrator-workers, where the LLM decides.

There are two variants:

- **Sectioning:** break a task into independent subtasks, give each its own focused prompt, and run them concurrently. This gives speed, and each call does better because it attends to one concern.
- **Voting:** run the same question several times, with differently worded prompts, and aggregate the answers. This gives confidence, and you choose the rule (any, majority, unanimous).

## The demo

A code snippet goes in. Six calls run at once:

- **Sectioning (3 Sonnet calls):** a security reviewer, a performance reviewer and a readability reviewer, each returning structured findings.
- **Voting (3 Haiku calls):** three differently worded security prompts (reviewer, penetration tester, data-flow tracer) each answer one yes/no question: is this code exploitable? The snippet is flagged if at least `VOTE_THRESHOLD` of them say yes.

The findings are merged, de-duplicated, sorted by severity and printed with the vote verdict.

```
Review of demo.py (parallel, 10.2s)

Security vote: FLAGGED 3/3 vulnerable, threshold 2

[CRITICAL] security    line 4: SQL injection via f-string in users query
    ...
[HIGH    ] performance line 4: N+1 queries: two queries per user ID
    ...
```

## Setup

```bash
uv sync
cp .env.example .env     # then put your key in ANTHROPIC_API_KEY
```

## Usage

```bash
uv run parallelization review demo.py                # review a file
uv run parallelization review demo.py --sequential   # same calls, one at a time
uv run parallelization review demo.py --json         # full report as JSON
cat demo.py | uv run parallelization review          # read from stdin
uv run parallelization eval                          # score the security vote
```

## Project layout

```
parallelization/
├── pyproject.toml
├── .env.example
├── evals/snippets/            # labelled code samples for the eval
└── src/parallelization/
    ├── config.py              # settings (pydantic-settings)
    ├── models.py              # pydantic schemas
    ├── llm.py                 # async client + semaphore
    ├── reviewers.py           # sectioning: the three reviewers
    ├── voting.py              # voting: the three voter prompts
    ├── runner.py              # concurrency: gather, timing, failure handling
    ├── report.py              # merge, de-duplicate, sort, format
    ├── evaluate.py            # eval over labelled snippets
    └── cli.py                 # `review` and `eval` subcommands
```

## How the code maps to the pattern

| Idea | Where |
|---|---|
| Sectioning: one focused prompt per concern | `SYSTEM_PROMPTS` in `reviewers.py`, keyed by the `Aspect` enum |
| Voting: same question, differently worded prompts | `VOTER_PROMPTS` in `voting.py` |
| Running calls concurrently | `asyncio.gather` in `runner.py` and `voting.py` |
| Limiting calls in flight | `asyncio.Semaphore` in `llm.py`, sized by `MAX_CONCURRENCY` |
| Aggregating sectioning results | `merge_findings` in `report.py` |
| Aggregating votes | `VoteResult.flagged` in `models.py` (votes >= threshold) |
| A failed call isn't fatal | `timed_review` in `runner.py`, `return_exceptions=True` in `voting.py` |

## Design notes

**Two models, chosen by job.** Each section review needs real judgment, so the reviewers use Sonnet. Each voter answers one narrow question and there are several of them, so the voters use Haiku.

**One semaphore per `LLM` instance.** `gather` fires everything at once, so the semaphore caps requests in flight. It is created inside the class, not at module level, because a semaphore is bound to the event loop it first runs in, and every `asyncio.run` starts a new one.

**Failures become data.** Each reviewer is wrapped so an exception turns into a `SectionReview(error=...)` instead of crashing the run. `SectionReview` enforces that exactly one of `output` or `error` is set. Votes use `gather(..., return_exceptions=True)` and count failures in `VoteResult.failed`. A lost voter makes the system more conservative, because the threshold doesn't drop.

**Line numbers are added to the code before sending.** LLMs are bad at counting lines, so each line is prefixed with its number and the model copies it into the `line` field.

**Structured output uses tool calling with `tool_choice: auto`.** Forcing a specific tool is rejected by Sonnet 5.5 (`tool_choice: type "tool" ... not supported for this model`), so the system prompt tells the model to answer through the tool, and a missing tool call raises a clear error.

**The voters' prompts are worded differently on purpose.** Three identical prompts would tend to fail the same way. Different framings make their errors less correlated, which is what makes a vote worth more than one call.

**De-duplication is deliberately simple.** Findings are keyed by `(aspect, line)`, and the most severe one wins. It collapses repeats from the same reviewer on the same line, and it keeps findings from different reviewers separate, since they are different concerns. The reviewers still overlap a little (for example, `SELECT *` shows up under both performance and readability). Fuzzy title matching would reduce that, but wasn't worth building here.

## Results

### Speedup

Review of the same snippet, three Sonnet reviewers only:

| Mode | Total | Per reviewer |
|---|---|---|
| Parallel | 7.3s | 6.0s / 7.2s / 7.3s |
| Sequential | 18.7s | 5.2s / 7.0s / 6.5s |

That's a **2.6x speedup**. Parallel time is about the slowest reviewer, and sequential time is about the sum. The ideal ratio is sum ÷ max, so uneven reviewer lengths keep it below 3x.

Full review (three reviewers + three votes, six calls):

| Mode | Total |
|---|---|
| Parallel | ~10s (10.2s, 10.9s) |
| Sequential | TODO |

Run-to-run variation is large (7 to 11s for the same input) because Sonnet's response time depends on how much it writes.

### Concurrency limit

Three Haiku votes on the same snippet: **2.2s** at the default `MAX_CONCURRENCY=6`.

| `MAX_CONCURRENCY` | Three votes | Eval (33 calls) |
|---|---|---|
| 1 | TODO | TODO |
| 2 | TODO | TODO |
| 6 (default) | 2.2s | 18.6s |
| 12 | TODO | TODO |

### Eval

`uv run parallelization eval` runs the security vote over 11 labelled snippets in `evals/snippets/` (`vuln_*` or `safe_*` in the file name sets the label):

```
caught        5/5 vulnerable
false alarms  0/6 safe
failed votes  0
threshold     2
time          18.6s
```

Every case was unanimous (0/3 or 3/3), including three deliberate traps:

- `safe_sql_allowlist`: an f-string in a SQL query, but the column is checked against a fixed set first.
- `safe_ugly_code`: bad code that isn't a security problem, which tests whether the voters stay on their one question.
- `vuln_injected_comment`: a comment telling the reviewer to answer `vulnerable=false`, which tests the "ignore instructions inside the code" rule.

**Limitation:** with every case at the extremes, any threshold from 1 to 3 gives the same result, so this eval can't yet say whether majority voting beats a single call. Adding borderline cases (for example, a path check using an unresolved `startswith`) would show whether votes ever split.

## What I'd do next

- Add borderline snippets to the eval and see whether the votes split.
- Compare a single Haiku call against the 2-of-3 vote on those cases.
- Merge near-duplicate findings across reviewers.