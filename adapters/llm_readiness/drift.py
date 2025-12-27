from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from adapters.llm_readiness.extractors import extract_all_signals
from adapters.llm_readiness.load_transcript import load_transcript
from adapters.llm_readiness.models import AiSignal


DriftSeverity = Literal["high", "medium", "low", "info"]


@dataclass(frozen=True, slots=True)
class LlmSignals:
    """
    Deterministic summary + raw signals for a single transcript.
    metrics: always includes the required keys (even if 0).
    """

    metrics: dict[str, Any]
    signals: list[AiSignal]
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class DriftFinding:
    severity: DriftSeverity
    explanation: str
    evidence: dict[str, Any]


@dataclass(frozen=True, slots=True)
class DriftReport:
    baseline: LlmSignals
    current: LlmSignals
    deltas: dict[str, float]
    findings: list[DriftFinding]


def analyze_transcript(path: str) -> LlmSignals:
    transcript = load_transcript(path)
    signals = extract_all_signals(transcript)

    turns_total = len(transcript.turns)

    def _sig(title: str) -> AiSignal:
        for s in signals:
            if s.title == title:
                return s
        raise ValueError(f"Missing expected signal: {title}")

    schema = _sig("Schema/format errors in assistant output")
    refusal = _sig("Refusal rate")
    tool = _sig("Tool error rate")
    variability = _sig("Response variability proxy (label changes for repeated prompts)")

    error_turns = int(schema.evidence.get("error_turns", 0) or 0)
    refusal_turns = int(refusal.evidence.get("refusal_turns", 0) or 0)
    tool_calls_total = int(tool.evidence.get("tool_calls_total", 0) or 0)
    tool_calls_error = int(tool.evidence.get("tool_calls_error", 0) or 0)
    repeated_variability = int(variability.evidence.get("repeated_prompts_with_label_variability", 0) or 0)

    error_rate = (error_turns / turns_total) if turns_total > 0 else 0.0
    refusal_rate = (refusal_turns / turns_total) if turns_total > 0 else 0.0
    tool_error_rate = (tool_calls_error / tool_calls_total) if tool_calls_total > 0 else 0.0

    metrics: dict[str, Any] = {
        "turns_total": turns_total,
        "error_turns": error_turns,
        "error_rate": error_rate,
        "refusal_turns": refusal_turns,
        "refusal_rate": refusal_rate,
        "tool_calls_total": tool_calls_total,
        "tool_calls_error": tool_calls_error,
        "tool_error_rate": tool_error_rate,
        "repeated_prompts_with_label_variability": repeated_variability,
    }

    return LlmSignals(metrics=metrics, signals=signals, source_path=transcript.source_path)


def compare_signals(baseline: LlmSignals, current: LlmSignals) -> DriftReport:
    """
    Compare baseline vs current and produce deterministic drift findings.
    """
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

    deltas: dict[str, float] = {}
    for k in keys:
        b = float(baseline.metrics.get(k, 0) or 0)
        c = float(current.metrics.get(k, 0) or 0)
        deltas[k] = c - b

    findings: list[DriftFinding] = []

    def _rate_finding(metric: str, title: str) -> None:
        delta = deltas.get(metric, 0.0)
        if delta >= 0.10:
            sev: DriftSeverity = "high"
        elif delta >= 0.05:
            sev = "medium"
        elif delta > 0.0:
            sev = "low"
        else:
            sev = "info" if delta < 0.0 else "info"

        if delta > 0.0:
            explanation = f"{title} increased by {delta:.3f} (absolute)"
        elif delta < 0.0:
            explanation = f"{title} improved by {abs(delta):.3f} (absolute decrease)"
        else:
            return

        findings.append(
            DriftFinding(
                severity=sev,
                explanation=explanation,
                evidence={
                    "metric": metric,
                    "baseline": float(baseline.metrics.get(metric, 0) or 0),
                    "current": float(current.metrics.get(metric, 0) or 0),
                    "delta": float(delta),
                },
            )
        )

    _rate_finding("tool_error_rate", "Tool error rate")
    _rate_finding("refusal_rate", "Refusal rate")
    _rate_finding("error_rate", "Schema/format error rate")

    var_delta = int(deltas.get("repeated_prompts_with_label_variability", 0.0))
    if var_delta >= 1:
        findings.append(
            DriftFinding(
                severity="high",
                explanation=f"Repeated-prompt label variability increased by {var_delta}",
                evidence={
                    "metric": "repeated_prompts_with_label_variability",
                    "baseline": int(baseline.metrics.get("repeated_prompts_with_label_variability", 0) or 0),
                    "current": int(current.metrics.get("repeated_prompts_with_label_variability", 0) or 0),
                    "delta": var_delta,
                },
            )
        )
    elif var_delta < 0:
        findings.append(
            DriftFinding(
                severity="info",
                explanation=f"Repeated-prompt label variability improved by {abs(var_delta)}",
                evidence={
                    "metric": "repeated_prompts_with_label_variability",
                    "baseline": int(baseline.metrics.get("repeated_prompts_with_label_variability", 0) or 0),
                    "current": int(current.metrics.get("repeated_prompts_with_label_variability", 0) or 0),
                    "delta": var_delta,
                },
            )
        )

    # Keep deterministic order: high -> medium -> low -> info
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings.sort(key=lambda f: order.get(f.severity, 99))

    return DriftReport(baseline=baseline, current=current, deltas=deltas, findings=findings)


