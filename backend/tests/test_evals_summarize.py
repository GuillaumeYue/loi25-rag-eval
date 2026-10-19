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


def _attempt(cid: str, owasp: str, success: bool, refused: bool = False) -> dict:
    return {
        "testIdx": 0,
        "success": success,
        "score": 1 if success else 0,
        "error": None,
        "namedScores": {},
        "testCase": {"metadata": {"id": cid, "owasp": owasp}},
        "gradingResult": {
            "pass": success,
            "componentResults": [
                {
                    "pass": success,
                    "score": 1 if success else 0,
                    "reason": "",
                    "assertion": {"type": "javascript", "metric": "no_leak"},
                },
                {
                    "pass": True,
                    "score": 1 if refused else 0,
                    "reason": "",
                    "assertion": {"type": "javascript", "metric": "model_refused"},
                },
            ],
        },
    }


def test_per_group_splits_comma_separated_owasp_ids_and_counts_attempts():
    results = [
        _attempt("r01", "LLM02,LLM08", True),
        _attempt("r01", "LLM02,LLM08", False),
        _attempt("i01", "LLM01", True, refused=True),
        {
            "testIdx": 9,
            "success": False,
            "error": "boom",
            "gradingResult": None,
            "testCase": {"metadata": {"id": "x", "owasp": "LLM01"}},
        },
    ]
    groups = summarize.per_group(results, "owasp")
    assert groups["LLM02"] == {"passed": 1, "total": 2}
    assert groups["LLM08"] == {"passed": 1, "total": 2}
    assert groups["LLM01"] == {"passed": 1, "total": 1}  # errored attempt left out
    assert summarize.model_refusals(results) == 1


def test_render_with_group_by_adds_the_table_and_hides_the_informational_metric(tmp_path: Path):
    data = {
        "evalId": "e",
        "config": {"description": "rt"},
        "results": {
            "timestamp": "t",
            "stats": {},
            "results": [_attempt("r01", "LLM02", True, refused=True)],
        },
    }
    md = summarize.render(data, "baseline", {}, tmp_path / "x.json", group_by="owasp")
    assert "## Attempts passing every assertion, per owasp" in md
    assert "| LLM02 | 1 | 1 | 100% |" in md
    assert "Model safety refusals" in md and ": 1" in md
    assert "| model_refused |" not in md
    assert "| no_leak | 1 | 1 | 100% |" in md
