# Routing

Pattern 3 from Anthropic's [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents).

## The pattern

A classifier call decides what kind of input this is, then code sends it to a
specialised handler. Each handler has its own focused prompt, and optionally
its own model. Tuning one handler can't degrade the others, which is the problem
with a single do-everything prompt.

The cost is that everything depends on the classifier. A confident wrong
classification sends the input to the wrong expert, and nothing downstream
notices.

## Demo: support-ticket router

Tickets for a fictional note-taking app, **Inkwell**, are classified on two axes:

- **Category** (`billing`, `technical`, `account`, `general`) picks the handler prompt.
- **Complexity** (`simple`, `complex`) picks the model: Haiku for simple, Sonnet for complex.

Tickets the classifier isn't confident about go to human review instead of a handler.

```
ticket ─► classify() ─► RouteDecision ─┬─ confidence < threshold ─► human review
          (Haiku, forced tool use)      │
                                        └─ confident ─► pick_model(complexity)
                                                        └─► handle(category prompt)
```

## Code map

| File | Role |
|---|---|
| `models.py` | `RouteDecision` schema: reasoning, category, complexity, confidence |
| `classifier.py` | One forced tool-use call that returns a validated `RouteDecision` |
| `handlers.py` | Shared base prompt plus one specialist prompt per category; `pick_model` |
| `router.py` | Applies the threshold, calls the handler, and returns a `RouteResult` |
| `evals.py` | Scores the classifier against labelled tickets |
| `cli.py` | `routing route` and `routing eval` |

## Running

```bash
uv sync
uv run routing route "I was charged twice this month."
uv run routing route --json "hi"
uv run routing eval
CONFIDENCE_THRESHOLD=0.9 uv run routing eval
```

Requires `ANTHROPIC_API_KEY` in `.env`.

## Design decisions

- **Structured output through forced tool use.** The pydantic schema becomes the
  tool's input schema. Field `description`s act as prompt text, and enums make
  invalid categories impossible to express.
- **`reasoning` is the first field**, so the model explains itself before it
  commits to a label.
- **Two paths to human review:** output that fails validation, or confidence below
  the threshold. API errors are not caught, because an outage should fail loudly
  rather than look like a hard ticket.
- **The router decides and the handlers execute.** Handlers receive their model
  rather than choosing it.

## Evaluation

`evals/tickets.jsonl` holds 15 labelled tickets: 12 clear and 3 marked
`ambiguous`, whose correct outcome is human review. The eval separates three kinds
of wrong, because they aren't equally bad:

- **Confident misroute.** The wrong expert answers. This is the dangerous one, and
  the eval exits 1 if any occur.
- **Missed ambiguous ticket.** A guess got through.
- **Needless review.** It costs human time but does no harm.

## What tuning taught me

- **Thresholds on round numbers are fragile.** The model reports values like 0.70
  and 0.75, so tickets sat exactly on the boundary and flipped between runs. I
  picked 0.8 from the data: clear tickets scored 0.85 or higher, and ambiguous
  ones 0.70 or lower.
- **Fix ambiguity in the prompt, not the threshold.** A pricing question kept
  landing at about 0.70 between billing and general. Saying explicitly that price
  questions are billing moved it to 0.95.
- **Fixes cause regressions.** Rewording the complexity definition fixed one
  ticket and flipped another. Without the eval I wouldn't have noticed.
- **Run evals more than once.** Results vary between runs, and one clean run
  proves little.
- **I found two bugs in the eval itself** by checking the summary against the
  per-ticket rows. An eval that miscounts is worse than none.

## Results

Across three runs at threshold 0.8: category accuracy 15/15, ambiguous → review
3/3, needless reviews 0/12, and no confident misroutes.

**Known limitation:** complexity is noisy. The Safari crash and the 40-person
evaluation ticket flip between `simple` and `complex`. This is accepted because
complexity only picks the model, not the expert. Improving it should start with
more borderline tickets in the eval set, not more prompt tweaks against two tickets.