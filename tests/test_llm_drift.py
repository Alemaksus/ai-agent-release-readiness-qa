from __future__ import annotations

from adapters.llm_readiness.drift import analyze_transcript, compare_signals
from adapters.llm_readiness.reporting import build_stability_section


def test_llm_drift_has_high_finding_and_markdown_contains_table() -> None:
    baseline = analyze_transcript("samples/llm_transcript_baseline.json")
    current = analyze_transcript("samples/llm_transcript.json")
    drift = compare_signals(baseline, current)

    assert any(f.severity == "high" for f in drift.findings)

    md = build_stability_section(
        transcript_path="samples/llm_transcript.json",
        baseline_transcript_path="samples/llm_transcript_baseline.json",
    )
    assert "Drift vs Baseline" in md
    assert "| Metric | Baseline | Current | Δ |" in md
    assert "`tool_error_rate`" in md



