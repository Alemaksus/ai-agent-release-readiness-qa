from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.models.test_case import TestCaseModel
from core.models.test_result import TestResultModel
from core.models.readiness import build_readiness_report
from core.reporting.exporter import save_markdown_report
from core.reporting.markdown_builder import build_markdown_report
from core.scoring.scorer import compute_metrics


@dataclass(frozen=True, slots=True)
class NormalizedData:
    """
    Minimal normalized container for smoke execution.

    This matches the contract used in core.scoring.scorer.compute_metrics(),
    where it iterates:
      - for r in data.results (expects r.id and r.status)
      - checks membership: r.id in data.test_cases
    So we store test_cases as dict[str, TestCaseModel] and results as list[TestResultModel].
    """

    test_cases: dict[str, TestCaseModel]
    results: list[TestResultModel]


def _build_smoke_data() -> NormalizedData:
    # 1) Define deterministic "existing test cases"
    test_cases_list = [
        TestCaseModel(id="TC-001", title="Login happy path", priority="P1", component="auth"),
        TestCaseModel(id="TC-002", title="Checkout happy path", priority="P1", component="payments"),
        TestCaseModel(id="TC-003", title="Refund intent", priority="P2", component="support"),
    ]

    # Make it a dict so:  "TC-001" in data.test_cases  -> True
    test_cases = {tc.id: tc for tc in test_cases_list}

    # 2) Define deterministic "existing run results"
    # IMPORTANT: status is plain str in TestResultModel, use the canonical values:
    # "passed" | "failed" | "skipped" | "error" (if your scorer supports it)
    results = [
        TestResultModel(id="TC-001", status="passed", duration_sec=1.23, raw_name="test_login_ok"),
        TestResultModel(id="TC-002", status="failed", duration_sec=4.50, raw_name="test_checkout_ok"),
        TestResultModel(id="TC-003", status="skipped", duration_sec=0.00, raw_name="test_refund_intent"),
        # Unmapped example (exists in results but not in test cases) — should affect coverage / unmapped stats
        TestResultModel(id="TC-999", status="failed", duration_sec=0.50, raw_name="test_unknown"),
    ]

    return NormalizedData(test_cases=test_cases, results=results)


def main() -> None:
    data = _build_smoke_data()

    metrics = compute_metrics(data)

    report = build_readiness_report(metrics)
    markdown = build_markdown_report(report)

    out_path = Path("reports") / "smoke_report.md"
    save_markdown_report(str(out_path), markdown)

    print(f"OK: saved smoke report to {out_path.resolve()}")


if __name__ == "__main__":
    main()
