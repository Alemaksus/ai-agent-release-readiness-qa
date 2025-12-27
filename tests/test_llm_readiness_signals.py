from __future__ import annotations

from adapters.llm_readiness.extractors import (
    extract_refusal_rate,
    extract_response_variability_proxy,
    extract_schema_format_errors,
    extract_tool_error_rate,
)
from adapters.llm_readiness.load_transcript import load_transcript


def test_llm_readiness_extractors_on_sample_transcript() -> None:
    t = load_transcript("samples/llm_transcript.json")

    schema_sig = extract_schema_format_errors(t)
    refusal_sig = extract_refusal_rate(t)
    tool_sig = extract_tool_error_rate(t)
    var_sig = extract_response_variability_proxy(t)

    # From samples/llm_transcript.json:
    # - schema errors: turn with expected_schema_valid=false, turn missing assistant_text, turn missing expected_schema_valid
    assert schema_sig.evidence["turns_total"] == 8
    assert schema_sig.evidence["error_turns"] == 3
    assert schema_sig.evidence["explicit_invalid"] == 1
    assert schema_sig.evidence["missing_assistant_text"] == 1
    assert schema_sig.evidence["missing_expected_schema_valid"] == 1

    # - refusals: exactly 1 turn
    assert refusal_sig.evidence["turns_total"] == 8
    assert refusal_sig.evidence["refusal_turns"] == 1

    # - tool calls: 3 total, 1 error
    assert tool_sig.evidence["tool_calls_total"] == 3
    assert tool_sig.evidence["tool_calls_error"] == 1

    # - variability: two repeated prompts have differing assistant_label values
    #   ("Generate a JSON report..." and "Call the tool to fetch artifacts.")
    assert var_sig.evidence["repeated_prompts_with_label_variability"] == 2


