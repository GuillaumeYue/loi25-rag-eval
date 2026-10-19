# Evals

promptfoo suites that call the backend over HTTP. Every run is recorded in
`results/` as the raw promptfoo JSON plus a Markdown summary, so the numbers in
the top-level README can be traced to a date, a model and a set of flags.

## Setup

```bash
cd evals && npm install          # pins promptfoo
npm test                         # unit tests for the JS assertions, no network
```

The backend must be running on `http://localhost:8000` with the provider you
want to measure (`LLM_PROVIDER=anthropic` for real numbers). The judge is
`claude-sonnet-5-5`, so `ANTHROPIC_API_KEY` must be set in the shell that runs
promptfoo.

## Accuracy suite

`promptfooconfig.accuracy.yaml` + `accuracy/cases.yaml` (40 cases).

```bash
cd evals
npm run eval:accuracy -- -o results/$(date +%F)-accuracy-baseline.json
../.venv/bin/python summarize.py results/$(date +%F)-accuracy-baseline.json --label baseline
```

Metrics (each assertion carries a `metric` name; the summary reports pass rate per metric):

| metric | cases | how it is scored |
|---|---|---|
| `retrieval_hit` | answerable | one of `expected_sources` is in the top-k sources |
| `cites_expected` | answerable | the answer cites a `[n]` whose source is an expected one |
| `has_citation` | answerable | the answer contains at least one `[n]` |
| `no_refusal` | answerable | the answer is not the refusal sentence |
| `correctness` | answerable | `llm-rubric`: contains the reference's essential information, no contradiction |
| `refusal` | unanswerable | the answer contains the exact refusal sentence |
| `no_fabrication` | unanswerable | `llm-rubric`: states the information is unavailable, asserts nothing |
| `no_tool_call` | all | no tool call on a plain question |

`cites_expected` is the headline RAG metric: the generation model has seen Loi 25
in training, so a correct answer alone does not prove the system worked; citing
the right article does.

Before a paid run, a run with `LLM_PROVIDER=stub` checks the wiring and acts as a
null baseline: the stub always answers a fixed sentence citing `[1]`, so
`correctness` should be near 0 and `refusal` 0. If the judge passes the stub,
the rubric is too lenient.

## Limits

- Cases were written by the project author from the article text; no production traffic.
- One repetition per run; differences of a few points are within run-to-run noise.
- 40 cases: one flaky case moves a rate by 2.5 to 3 points.
