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


# Assertions that measure one specific category, whatever else the case is
# tagged with. The leak probes r01-r06 are tagged "LLM02,LLM08": the answer must
# not reveal internal facts (LLM02) AND no interne chunk may be retrieved for a
# public caller (LLM08). Without this map a retrieval-level failure would also
# count as an LLM02 failure, and an output filter that stops every leaked fact
# would still show 0% on LLM02.
METRIC_SCOPE = {"no_internal_source": "LLM08"}
INFORMATIONAL = {"model_refused"}


def _metric(comp: dict[str, Any]) -> str:
    assertion = comp.get("assertion") or {}
    return str(assertion.get("metric") or assertion.get("type"))


def per_group(results: list[dict[str, Any]], key: str) -> OrderedDict[str, dict[str, int]]:
    """Attempts, and attempts passing every relevant assertion, per metadata value.

    A comma-separated value (e.g. owasp "LLM02,LLM08") counts under each entry.
    For each entry the relevant assertions are the case's assertions minus those
    METRIC_SCOPE assigns to another entry; an entry that METRIC_SCOPE targets
    only counts its own scoped assertions. Errored attempts are left out.
    """
    groups: OrderedDict[str, dict[str, int]] = OrderedDict()
    scoped_groups = set(METRIC_SCOPE.values())
    for res in results:
        grading = res.get("gradingResult")
        if res.get("error") and not grading:
            continue
        comps = [
            c
            for c in (grading or {}).get("componentResults") or []
            if _metric(c) not in INFORMATIONAL
        ]
        meta = (res.get("testCase") or {}).get("metadata") or {}
        for value in (v.strip() for v in str(meta.get(key) or "untagged").split(",")):
            if value in scoped_groups:
                relevant = [c for c in comps if METRIC_SCOPE.get(_metric(c)) == value]
            else:
                relevant = [c for c in comps if _metric(c) not in METRIC_SCOPE]
            if not relevant and comps:
                continue  # nothing in this case measures this entry
            g = groups.setdefault(value, {"passed": 0, "total": 0})
            g["total"] += 1
            passed = all(c.get("pass") for c in relevant) if relevant else bool(res.get("success"))
            if passed:
                g["passed"] += 1
    return groups


def model_refusals(results: list[dict[str, Any]]) -> int:
    """Attempts where the informational `model_refused` assertion scored 1."""
    n = 0
    for res in results:
        for comp in (res.get("gradingResult") or {}).get("componentResults") or []:
            if (comp.get("assertion") or {}).get("metric") == "model_refused" and comp.get("score"):
                n += 1
    return n


def judge_model(data: dict[str, Any]) -> str:
    options = ((data.get("config") or {}).get("defaultTest") or {}).get("options") or {}
    provider = options.get("provider")
    if isinstance(provider, dict):
        return str(provider.get("id"))
    return str(provider or "n/a")


def render(
    data: dict[str, Any],
    label: str,
    backend: dict[str, Any],
    source: Path,
    group_by: str | None = None,
) -> str:
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
    ]
    refusals = model_refusals(results)
    if refusals:
        lines.append(
            f"- Model safety refusals (counted as pass, listed for transparency): {refusals}"
        )
    if group_by:
        lines += [
            "",
            f"## Attempts passing every relevant assertion, per {group_by}",
            "",
            f"| {group_by} | passed | attempts | rate |",
            "|---|---:|---:|---:|",
        ]
        for name, g in per_group(results, group_by).items():
            rate = f"{100 * g['passed'] / g['total']:.0f}%" if g["total"] else "n/a"
            lines.append(f"| {name} | {g['passed']} | {g['total']} | {rate} |")
    lines += [
        "",
        "## Pass rate per metric",
        "",
        "| metric | passed | total | rate |",
        "|---|---:|---:|---:|",
    ]
    for name, m in metrics.items():
        if name == "model_refused":
            continue  # informational, always passes; reported above
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
    parser.add_argument("--group-by", help="metadata key for a per-group table, e.g. owasp")
    args = parser.parse_args(argv)

    data = load_results(args.results)
    report = render(data, args.label, backend_info(args.backend), args.results, args.group_by)
    out = args.out or args.results.with_suffix(".md")
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
