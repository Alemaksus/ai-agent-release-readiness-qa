# AI/LLM Stability Semantics (Advisory)

This repository provides a deterministic QA-based release readiness core and an optional AI/LLM stability layer.
The AI/LLM layer is designed to add context to the report **without changing** the deterministic core score.

## 1) Purpose of the AI/LLM stability layer
The AI/LLM stability layer exists to detect and communicate runtime reliability risks that are specific to AI-agent
behavior and tooling, such as:
- tool execution failures (e.g. tool calls returning error)
- schema/format violations (breaking output contracts)
- refusal behavior changes
- response variability for repeated prompts (proxy)

These signals are computed deterministically from transcript JSON inputs and are intended to support QA review,
incident prevention, and release governance.

## 2) Advisory-only nature of AI drift
AI/LLM stability signals are **advisory only**:
- They **MUST NOT** directly modify the deterministic core readiness score.
- They **MAY** add warnings/findings to the report.
- They **MAY** influence recommendation wording in narrative form (e.g. “HOLD for investigation”), while remaining
  explicitly advisory.
- They **MAY** elevate perceived risk in the narrative (e.g. “core score is good, but AI stability risks increased”).

The core score remains fully reproducible from the QA metrics alone.

## 3) Signal priority and rationale (defensible hierarchy)
When presenting or interpreting AI/LLM stability risks, use this priority order:

1. **Tool error rate** (highest priority)  
   Tool execution failures can break automation pipelines and can cause silent or partial failures.
2. **Schema/format error rate**  
   Schema violations break output contracts and downstream parsing, often leading to incorrect automation outcomes.
3. **Refusal rate** (lowest priority among the three)  
   Refusals are generally visible and safer than malformed actions; they still impact usability and flow completion.

Other signals (e.g. response variability proxies) are supportive indicators and should not supersede the hierarchy above.

## 4) Schema contract guarantees
Schema/format violations are treated as a **contract breach**.

**Policy guarantee:** any detected schema/format violation is classified as **HIGH severity** (unconditional).
This applies to single-run signals regardless of frequency.

## 5) Baseline definition and fallback behavior
For drift/regression analysis, the baseline is defined as:
- **Baseline:** the last **approved release** transcript (golden reference).

If a golden baseline is not available, comparison against the **previous run** is permitted only as a fallback and must
be explicitly stated as such in the report.

In this repository’s CLI:
- Drift comparison is enabled by providing both `--baseline-transcript` (baseline) and `--transcript` (current).
- If no baseline is provided, the report includes **current-only** AI/LLM stability signals and does not claim drift.

## 6) Practical interpretation examples

### Example A: Good core score, but AI stability warrants HOLD (advisory)
- Core readiness: score 92 / risk LOW.
- AI stability: tool error rate increased significantly vs baseline.

Interpretation: the release may still be “core-ready”, but tooling instability is a deployment risk.
Recommendation wording in the report may state **HOLD for investigation** (advisory), while the deterministic core score
remains unchanged.

### Example B: Core score is moderate, AI drift shows improvements (advisory)
- Core readiness: score 75 / risk MEDIUM.
- AI drift: schema/format errors decreased vs baseline; tool errors unchanged.

Interpretation: AI stability improvements reduce one category of operational risk, but the core readiness decision still
comes from QA metrics; the report may include an “improvement” note for traceability.


