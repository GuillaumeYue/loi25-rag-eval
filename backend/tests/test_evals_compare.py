"""evals/compare.py on synthetic matrix files (no promptfoo, no network)."""

import json
from pathlib import Path

import compare


def _attempt(owasp: str, success: bool, metric: str = "no_leak") -> dict:
    return {
        "success": success,
        "error": None,
        "testCase": {"metadata": {"id": "x", "owasp": owasp}},
        "gradingResult": {
            "pass": success,
            "componentResults": [
                {
                    "pass": success,
                    "score": int(success),
                    "reason": "",
                    "assertion": {"metric": metric},
                }
            ],
        },
    }


def _write(dirpath: Path, name: str, payload: dict) -> None:
    (dirpath / name).write_text(json.dumps(payload), encoding="utf-8")


def test_render_builds_one_column_per_label(tmp_path: Path):
    d = "2026-10-20"
    for label, ok in (("baseline", False), ("acl", True)):
        _write(
            tmp_path,
            f"{d}-redteam-{label}.json",
            {"results": {"results": [_attempt("LLM02,LLM08", ok), _attempt("control", True)]}},
        )
        _write(
            tmp_path,
            f"{d}-accuracy-{label}.json",
            {"results": {"results": [_attempt("n/a", True, metric="correctness")]}},
        )
        _write(
            tmp_path,
            f"{d}-health-{label}.json",
            {
                "model": "claude-haiku-5-5",
                "embedding_provider": "fastembed",
                "top_k": 5,
                "flags": {"ENFORCE_ACCESS_CONTROL": label == "acl", "TOOL_GUARD": False},
            },
        )

    md = compare.render(d, ["baseline", "acl", "isolate"], tmp_path)
    assert "| | baseline | acl | isolate |" in md
    assert "- `baseline`: none" in md
    assert "- `acl`: ENFORCE_ACCESS_CONTROL" in md
    assert "| LLM02 – Sensitive Information Disclosure (n=1) | 0% | 100% | n/a |" in md
    assert (
        "| control – controls (employee access, legitimate email) (n=1) | 100% | 100% | n/a |" in md
    )
    assert "| all – every red-team attempt (n=2) | 50% | 100% | n/a |" in md
    assert "| correctness – LLM-as-judge vs reference (n=1) | 100% | 100% | n/a |" in md
    assert "Model under test: claude-haiku-5-5" in md


def test_main_writes_the_comparison_file(tmp_path: Path):
    assert (
        compare.main(
            ["--date", "2026-01-01", "--labels", "baseline", "--results-dir", str(tmp_path)]
        )
        == 0
    )
    assert (tmp_path / "2026-01-01-comparison.md").exists()
