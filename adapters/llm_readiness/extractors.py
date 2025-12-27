from __future__ import annotations

from collections import defaultdict

from adapters.llm_readiness.models import AiSignal, Transcript


def extract_schema_format_errors(transcript: Transcript) -> AiSignal:
    """
    Count turns where assistant output is schema-invalid or missing required fields.

    Rule:
      schema/format error if expected_schema_valid is False OR expected_schema_valid is missing/invalid OR assistant_text is missing
    """
    error_turns = 0
    missing_expected_schema_valid = 0
    missing_assistant_text = 0
    explicit_invalid = 0

    for t in transcript.turns:
        if t.expected_schema_valid is False:
            explicit_invalid += 1
        if t.expected_schema_valid is None:
            missing_expected_schema_valid += 1
        if t.assistant_text is None or t.assistant_text.strip() == "":
            missing_assistant_text += 1

        if (t.expected_schema_valid is False) or (t.expected_schema_valid is None) or (
            t.assistant_text is None or t.assistant_text.strip() == ""
        ):
            error_turns += 1

    severity = "high" if error_turns >= 3 else ("medium" if error_turns >= 1 else "low")

    return AiSignal(
        severity=severity,
        title="Schema/format errors in assistant output",
        evidence={
            "turns_total": len(transcript.turns),
            "error_turns": error_turns,
            "explicit_invalid": explicit_invalid,
            "missing_expected_schema_valid": missing_expected_schema_valid,
            "missing_assistant_text": missing_assistant_text,
        },
    )


def extract_refusal_rate(transcript: Transcript) -> AiSignal:
    refusal_turns = sum(1 for t in transcript.turns if t.refusal is True)
    total = len(transcript.turns)
    rate = (refusal_turns / total) if total > 0 else 0.0

    severity = "high" if rate >= 0.3 else ("medium" if rate > 0.0 else "low")
    return AiSignal(
        severity=severity,
        title="Refusal rate",
        evidence={
            "turns_total": total,
            "refusal_turns": refusal_turns,
            "refusal_rate": rate,
        },
    )


def extract_tool_error_rate(transcript: Transcript) -> AiSignal:
    total_calls = 0
    error_calls = 0

    for t in transcript.turns:
        calls = t.tool_calls or []
        for c in calls:
            if not isinstance(c, dict):
                continue
            total_calls += 1
            status = c.get("status")
            if status == "error":
                error_calls += 1

    rate = (error_calls / total_calls) if total_calls > 0 else 0.0
    severity = "high" if rate >= 0.2 else ("medium" if rate > 0.0 else "low")
    return AiSignal(
        severity=severity,
        title="Tool error rate",
        evidence={
            "tool_calls_total": total_calls,
            "tool_calls_error": error_calls,
            "tool_error_rate": rate,
        },
    )


def extract_response_variability_proxy(transcript: Transcript) -> AiSignal:
    """
    Proxy for response variability:
      same user_text repeated with different assistant_label (if assistant_label is present).
    """
    labels_by_user_text: dict[str, set[str]] = defaultdict(set)

    for t in transcript.turns:
        if t.user_text is None:
            continue
        if t.assistant_label is None:
            continue
        labels_by_user_text[t.user_text].add(t.assistant_label)

    variable_prompts = {ut: labels for ut, labels in labels_by_user_text.items() if len(labels) > 1}
    variable_count = len(variable_prompts)

    severity = "high" if variable_count >= 2 else ("medium" if variable_count == 1 else "low")
    return AiSignal(
        severity=severity,
        title="Response variability proxy (label changes for repeated prompts)",
        evidence={
            "repeated_prompts_with_label_variability": variable_count,
            "examples": {k: sorted(v) for k, v in list(variable_prompts.items())[:3]},
        },
    )


def extract_all_signals(transcript: Transcript) -> list[AiSignal]:
    return [
        extract_schema_format_errors(transcript),
        extract_refusal_rate(transcript),
        extract_tool_error_rate(transcript),
        extract_response_variability_proxy(transcript),
    ]


