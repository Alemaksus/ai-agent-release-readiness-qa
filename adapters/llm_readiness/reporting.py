from __future__ import annotations

from pathlib import Path
from typing import Any

from adapters.llm_readiness.drift import DriftReport, analyze_transcript, compare_signals
from adapters.llm_readiness.summarize import signals_to_markdown


def build_stability_section(*, transcript_path: str | Path, baseline_transcript_path: str | Path | None = None) -> str:
    """
    Build the optional markdown section appended at CLI layer.
    """
    current = analyze_transcript(str(transcript_path))

    lines: list[str] = []
    lines.append("## AI/LLM Stability Signals (optional)")
    lines.append("")
    lines.append("_Advisory only: does not modify the deterministic core readiness score._")
    lines.append("")
    lines.append(signals_to_markdown(current.signals).rstrip())
    lines.append("")

    if baseline_transcript_path:
        baseline = analyze_transcript(str(baseline_transcript_path))
        drift = compare_signals(baseline, current)
        lines.extend(_drift_markdown(drift))

    return "\n".join(lines).rstrip() + "\n"


def _fmt(v: Any) -> str:
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _drift_markdown(drift: DriftReport) -> list[str]:
    keys = [
        "turns_total",
        "error_turns",
        "error_rate",
        "refusal_turns",
        "refusal_rate",
        "tool_calls_total",
        "tool_calls_error",
        "tool_error_rate",
        "repeated_prompts_with_label_variability",
    ]

    out: list[str] = []
    out.append("### Drift vs Baseline (optional)")
    out.append("")
    out.append("| Metric | Baseline | Current | Δ |")
    out.append("|---|---:|---:|---:|")
    for k in keys:
        b = drift.baseline.metrics.get(k, 0)
        c = drift.current.metrics.get(k, 0)
        d = drift.deltas.get(k, 0.0)
        out.append(f"| `{k}` | {_fmt(b)} | {_fmt(c)} | {_fmt(d)} |")
    out.append("")

    out.append("#### Findings")
    out.append("")
    if drift.findings:
        for f in drift.findings:
            out.append(f"- **{f.severity.upper()}**: {f.explanation}")
    else:
        out.append("- _No drift detected._")
    out.append("")
    return out



