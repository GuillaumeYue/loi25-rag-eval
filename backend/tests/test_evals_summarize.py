"""evals/summarize.py against a trimmed promptfoo output (fixture captured from a real run)."""

import json
from pathlib import Path

import summarize

FIXTURE = Path(__file__).parent / "fixtures" / "promptfoo-smoke.json"


def test_per_metric_counts_only_cases_where_the_assertion_ran():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    metrics = summarize.per_metric(data["results"]["results"])
    assert metrics["retrieval_hit"]["passed"] == 1 and metrics["retrieval_hit"]["total"] == 1
    assert metrics["refusal"]["passed"] == 0 and metrics["refusal"]["total"] == 1
    assert metrics["refusal"]["failures"][0][0] == "s02"
    assert "no refusal sentence" in metrics["refusal"]["failures"][0][1]


def test_errored_cases_are_listed_not_scored():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    errors = summarize.errored(data["results"]["results"])
    assert errors == [("s03", "Error: connect ECONNREFUSED")]


def test_render_mentions_backend_info_judge_and_rates(tmp_path: Path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    backend = {
        "llm_provider": "anthropic",
        "model": "claude-haiku-5-5",
        "embedding_provider": "fastembed",
        "top_k": 5,
        "flags": {"ENFORCE_ACCESS_CONTROL": False},
    }
    md = summarize.render(data, "baseline", backend, tmp_path / "x.json")
    assert "# baseline: smoke" in md
    assert "Model under test: claude-haiku-5-5 (provider anthropic)" in md
    assert "Judge: anthropic:messages:claude-sonnet-5-5" in md
    assert "| retrieval_hit | 1 | 1 | 100% |" in md
    assert "| refusal | 0 | 1 | 0% |" in md
    assert "Cases: 3 (2 scored, 1 errored)" in md
    assert "- `s03`: Error: connect ECONNREFUSED" in md
    assert '"ENFORCE_ACCESS_CONTROL": false' in md


def test_main_writes_markdown_next_to_json(tmp_path: Path, capsys):
    src = tmp_path / "run.json"
    src.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    # --backend "" skips the /health call, so the test needs no server.
    assert summarize.main([str(src), "--label", "test", "--backend", ""]) == 0
    out = tmp_path / "run.md"
    assert out.exists()
    assert "Model under test: unknown" in out.read_text(encoding="utf-8")
