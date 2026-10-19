"""Turn a promptfoo JSON output into a short Markdown report next to it.

    python summarize.py results/2026-10-19-accuracy-baseline.json [--label baseline]
                        [--backend http://localhost:8000]

The report records what README numbers need to be traceable: date, suite,
model and flags under test (read from the backend's /health while it is still
up, or "unknown"), judge model, pass rate per metric, failing cases with the
grader's reason, and cases that errored (infrastructure, not model failures).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


def load_results(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def backend_info(url: str | None) -> dict[str, Any]:
    if not url:
        return {}
    try:
        with urlopen(f"{url.rstrip('/')}/health", timeout=5) as resp:  # noqa: S310 (local URL)
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, ValueError):
        return {}


def case_id(result: dict[str, Any]) -> str:
    meta = (result.get("testCase") or {}).get("metadata") or {}
    return str(meta.get("id") or result.get("testIdx"))


def per_metric(results: list[dict[str, Any]]) -> OrderedDict[str, dict[str, Any]]:
    """Pass counts per `metric`, counting only cases where that assertion ran."""
    metrics: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for res in results:
        if res.get("error") and not res.get("gradingResult"):
            continue  # infrastructure error: reported separately, not a failure
        grading = res.get("gradingResult") or {}
        for comp in grading.get("componentResults") or []:
            name = (comp.get("assertion") or {}).get("metric") or (comp.get("assertion") or {}).get(
                "type"
            )
            m = metrics.setdefault(name, {"passed": 0, "total": 0, "failures": []})
            m["total"] += 1
            if comp.get("pass"):
                m["passed"] += 1
            else:
                m["failures"].append((case_id(res), str(comp.get("reason") or "")[:160]))
    return metrics


def errored(results: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [
        (case_id(r), str(r.get("error"))[:160])
        for r in results
        if r.get("error") and not r.get("gradingResult")
    ]


def judge_model(data: dict[str, Any]) -> str:
    options = ((data.get("config") or {}).get("defaultTest") or {}).get("options") or {}
    provider = options.get("provider")
    if isinstance(provider, dict):
        return str(provider.get("id"))
    return str(provider or "n/a")


def render(data: dict[str, Any], label: str, backend: dict[str, Any], source: Path) -> str:
    body = data["results"]
    results = body["results"]
    stats = body.get("stats") or {}
    metrics = per_metric(results)
    errors = errored(results)
    scored = len(results) - len(errors)
    passed = sum(1 for r in results if r.get("success"))
    when = body.get("timestamp") or datetime.now(UTC).isoformat()

    lines = [
        f"# {label}: {(data.get('config') or {}).get('description', 'promptfoo run')}",
        "",
        f"- Date: {when}",
        f"- Eval id: {data.get('evalId', 'n/a')}",
        f"- Source: `{source.name}`",
        f"- Model under test: {backend.get('model') or 'unknown'} "
        f"(provider {backend.get('llm_provider', 'unknown')})",
        f"- Embeddings: {backend.get('embedding_provider', 'unknown')}, "
        f"top-k {backend.get('top_k', 'unknown')}",
        f"- Mitigation flags: {json.dumps(backend.get('flags', 'unknown'))}",
        f"- Judge: {judge_model(data)}",
        f"- Cases: {len(results)} ({scored} scored, {len(errors)} errored)",
        f"- All assertions passed: {passed}/{scored}"
        + (f" ({100 * passed / scored:.0f}%)" if scored else ""),
        f"- Duration: {stats.get('durationMs', 'n/a')} ms",
        "",
        "## Pass rate per metric",
        "",
        "| metric | passed | total | rate |",
        "|---|---:|---:|---:|",
    ]
    for name, m in metrics.items():
        rate = f"{100 * m['passed'] / m['total']:.0f}%" if m["total"] else "n/a"
        lines.append(f"| {name} | {m['passed']} | {m['total']} | {rate} |")

    lines += ["", "## Failures", ""]
    any_failure = False
    for name, m in metrics.items():
        if not m["failures"]:
            continue
        any_failure = True
        lines.append(f"### {name}")
        lines.append("")
        for cid, reason in m["failures"]:
            lines.append(f"- `{cid}`: {reason}")
        lines.append("")
    if not any_failure:
        lines.append("None.")
        lines.append("")

    if errors:
        lines += ["## Errored cases (not scored)", ""]
        for cid, err in errors:
            lines.append(f"- `{cid}`: {err}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("results", type=Path, help="promptfoo JSON output (-o file.json)")
    parser.add_argument("--label", default="baseline", help="run label for the report title")
    parser.add_argument(
        "--backend", default="http://localhost:8000", help="backend URL for /health"
    )
    parser.add_argument("--out", type=Path, help="markdown path (default: next to the JSON)")
    args = parser.parse_args(argv)

    data = load_results(args.results)
    report = render(data, args.label, backend_info(args.backend), args.results)
    out = args.out or args.results.with_suffix(".md")
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
