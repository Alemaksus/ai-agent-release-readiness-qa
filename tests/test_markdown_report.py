from __future__ import annotations

from core.models.readiness import build_readiness_report
from core.reporting.markdown_builder import build_markdown_report


def test_markdown_contains_required_sections_and_risk() -> None:
    metrics = {
        "total_cases": 3,
        "total_results": 4,
        "mapped_results": 3,
        "unmapped_results": 1,
        "passed": 1,
        "failed": 1,
        "skipped": 1,
        "failure_rate": 1 / 3,
        "skip_rate": 1 / 3,
    }

    report = build_readiness_report(metrics)
    md = build_markdown_report(report)

    assert "Release Readiness" in md  # header contains this phrase
    assert "## Metrics" in md
    assert "## Assumptions" in md
    assert "high" in md  # risk level text


