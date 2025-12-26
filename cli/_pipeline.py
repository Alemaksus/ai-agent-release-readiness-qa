from __future__ import annotations

from pathlib import Path

from core.models.normalized import NormalizedData
from core.models.normalizer import normalize
from core.models.readiness import build_readiness_report
from core.models.test_case import TestCaseModel
from core.models.test_result import TestResultModel
from core.parsers.csv_loader import load_test_cases_csv
from core.parsers.junit_loader import load_junit_results
from core.reporting.exporter import save_markdown_report
from core.reporting.markdown_builder import build_markdown_report
from core.scoring.scorer import compute_metrics


def _build_demo_data() -> NormalizedData:
    test_cases_list = [
        TestCaseModel(
            id="TC-001",
            title="Login works",
            priority="high",
            component="auth",
            description="Basic login should succeed with valid credentials.",
        ),
        TestCaseModel(
            id="TC-002",
            title="Checkout works",
            priority="high",
            component="payments",
            description="Checkout should succeed for an in-stock item with valid payment method.",
        ),
        TestCaseModel(
            id="TC-003",
            title="Refund intent supported",
            priority="medium",
            component="support",
            description="User asks for refund; system should route to correct policy/flow.",
        ),
    ]

    results = [
        TestResultModel(id="TC-001", status="passed", duration_sec=1.23, raw_name="test_login_ok"),
        TestResultModel(id="TC-002", status="failed", duration_sec=4.50, raw_name="test_checkout_ok"),
        TestResultModel(id="TC-003", status="skipped", duration_sec=0.00, raw_name="test_refund_intent"),
        # Unmapped example (exists in results but not in test cases) — should affect coverage / unmapped stats
        TestResultModel(id="TC-999", status="failed", duration_sec=0.50, raw_name="test_unknown"),
    ]

    return NormalizedData(
        test_cases={tc.id: tc for tc in test_cases_list},
        results=results,
    )


def run_demo(out_path: str | Path) -> Path:
    """
    Deterministic demo pipeline:
      demo data -> compute_metrics -> build_readiness_report -> build_markdown_report -> save_markdown_report
    """
    out_path = Path(out_path)

    data = _build_demo_data()
    metrics = compute_metrics(data)
    report = build_readiness_report(metrics)
    markdown = build_markdown_report(report)
    save_markdown_report(str(out_path), markdown)

    return out_path


def run_from_files(*, cases_path: str | Path, junit_path: str | Path, out_path: str | Path) -> Path:
    """
    Deterministic file-based pipeline:
      parse CSV + JUnit -> normalize -> compute_metrics -> build_readiness_report -> build_markdown_report -> save_markdown_report
    """
    out_path = Path(out_path)

    test_case_dicts = load_test_cases_csv(str(cases_path))
    result_dicts = load_junit_results(str(junit_path))
    data = normalize(test_case_dicts, result_dicts)

    metrics = compute_metrics(data)
    report = build_readiness_report(metrics)
    markdown = build_markdown_report(report)
    save_markdown_report(str(out_path), markdown)

    return out_path


