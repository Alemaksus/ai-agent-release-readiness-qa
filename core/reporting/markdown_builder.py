from __future__ import annotations

from datetime import datetime

from core.models.readiness import ReadinessReport


def build_markdown_report(report: ReadinessReport) -> str:
    """
    Render a deterministic Markdown report.

    Includes: title, score/risk, metrics table, and highlights.
    """
    generated_at = datetime.utcnow()

    score = int(report.score.overall_score)
    risk = report.score.risk_level.value
    recommendation = report.score.recommendation.value

    lines: list[str] = []
    lines.append("# Release Readiness Smoke Report")
    lines.append("")
    lines.append(f"- Generated at (UTC): `{generated_at.isoformat(timespec='seconds')}`")
    lines.append(f"- Readiness score: **{score} / 100**")
    lines.append(f"- Risk level: **{risk}**")
    lines.append(f"- Recommendation: **{recommendation}**")
    lines.append("")

    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    for k in sorted(report.metrics.keys()):
        lines.append(f"| `{k}` | {report.metrics[k]} |")
    lines.append("")

    lines.append("## Highlights")
    lines.append("")
    if report.risks:
        for r in report.risks:
            sev = r.severity.value
            lines.append(f"- **{sev}**: {r.description}")
            for ev in r.evidence:
                lines.append(f"  - {ev}")
    else:
        lines.append("_No highlights._")
    lines.append("")

    lines.append("## Assumptions")
    lines.append("")
    for a in report.assumptions:
        lines.append(f"- {a}")
    lines.append("")

    return "\n".join(lines)
