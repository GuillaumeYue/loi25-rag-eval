"""Build the baseline-vs-mitigation table from one day's matrix results.

    python compare.py --date 2026-10-20 [--labels baseline,acl,...]

Reads results/<date>-{accuracy,redteam}-<label>.json and
results/<date>-health-<label>.json (written by run_matrix.sh) and writes
results/<date>-comparison.md. Rates come from summarize.py's own counting, so
the table and the per-run reports cannot disagree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import summarize

RESULTS = Path(__file__).parent / "results"
DEFAULT_LABELS = ["baseline", "acl", "isolate", "toolguard", "outfilter", "all"]

ACCURACY_ROWS = [
    ("retrieval_hit", "expected article in top-5"),
    ("cites_expected", "answer cites the expected article"),
    ("correctness", "LLM-as-judge vs reference"),
    ("no_refusal", "answerable question not refused"),
    ("refusal", "out-of-corpus question refused"),
    ("no_tool_call", "no tool call on a plain question"),
]
REDTEAM_ROWS = [
    ("LLM01", "Prompt Injection"),
    ("LLM02", "Sensitive Information Disclosure"),
    ("LLM06", "Excessive Agency"),
    ("LLM07", "System Prompt Leakage"),
    ("LLM08", "Vector and Embedding Weaknesses"),
    ("LLM09", "Misinformation"),
    ("control", "controls (employee access, legitimate email)"),
]


def _load(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _rate(passed: int, total: int) -> str:
    return f"{100 * passed / total:.0f}%" if total else "n/a"


def accuracy_cells(data: dict[str, Any] | None) -> dict[str, tuple[int, int]]:
    if data is None:
        return {}
    metrics = summarize.per_metric(data["results"]["results"])
    return {name: (m["passed"], m["total"]) for name, m in metrics.items()}


def redteam_cells(data: dict[str, Any] | None) -> dict[str, tuple[int, int]]:
    if data is None:
        return {}
    results = data["results"]["results"]
    cells = {k: (g["passed"], g["total"]) for k, g in summarize.per_group(results, "owasp").items()}
    scored = [r for r in results if r.get("gradingResult")]
    cells["all"] = (sum(1 for r in scored if r.get("success")), len(scored))
    cells["_refusals"] = (summarize.model_refusals(results), len(scored))
    return cells


def _row(name: str, note: str, cells_by_label: dict[str, dict], labels: list[str]) -> str:
    sizes = {cells[name][1] for cells in cells_by_label.values() if name in cells}
    n = "/".join(str(s) for s in sorted(sizes)) or "0"
    values = [
        _rate(*cells_by_label[label][name]) if name in cells_by_label.get(label, {}) else "n/a"
        for label in labels
    ]
    return f"| {name} – {note} (n={n}) | " + " | ".join(values) + " |"


def render(date: str, labels: list[str], results_dir: Path = RESULTS) -> str:
    acc = {lb: accuracy_cells(_load(results_dir / f"{date}-accuracy-{lb}.json")) for lb in labels}
    red = {lb: redteam_cells(_load(results_dir / f"{date}-redteam-{lb}.json")) for lb in labels}
    health = {lb: _load(results_dir / f"{date}-health-{lb}.json") or {} for lb in labels}
    base = health.get(labels[0], {})

    head = "| | " + " | ".join(labels) + " |"
    sep = "|---|" + "---:|" * len(labels)
    lines = [
        f"# Baseline vs mitigations, {date}",
        "",
        f"- Model under test: {base.get('model', 'unknown')}, embeddings "
        f"{base.get('embedding_provider', 'unknown')}, top-k {base.get('top_k', 'unknown')}",
        "- Judge: anthropic:messages:claude-sonnet-5-5",
        "- Accuracy: 40 cases, one run. Red team: 26 cases × 3 runs, rates per attempt.",
        "",
        "Flags per column (from each backend's /health):",
        "",
    ]
    for lb in labels:
        on = [k for k, v in (health[lb].get("flags") or {}).items() if v]
        lines.append(f"- `{lb}`: {', '.join(on) if on else 'none'}")
    lines += ["", "## Red team: attempts passing every assertion", "", head, sep]
    lines += [_row(k, note, red, labels) for k, note in REDTEAM_ROWS]
    lines.append(_row("all", "every red-team attempt", red, labels))
    lines += ["", "## Accuracy: pass rate per metric", "", head, sep]
    lines += [_row(k, note, acc, labels) for k, note in ACCURACY_ROWS]
    refusals = [str(red[lb].get("_refusals", (0, 0))[0]) for lb in labels]
    lines += [
        "",
        "Model safety refusals during the red team (counted as passes): "
        + ", ".join(f"{lb} {n}" for lb, n in zip(labels, refusals, strict=True))
        + ".",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--date", required=True)
    parser.add_argument("--labels", default=",".join(DEFAULT_LABELS))
    parser.add_argument("--results-dir", type=Path, default=RESULTS)
    args = parser.parse_args(argv)
    labels = [lb.strip() for lb in args.labels.split(",") if lb.strip()]
    report = render(args.date, labels, args.results_dir)
    out = args.results_dir / f"{args.date}-comparison.md"
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
