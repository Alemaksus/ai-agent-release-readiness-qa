from __future__ import annotations

import pytest

from core.models.normalized import NormalizedData
from core.models.test_case import TestCaseModel as CaseModel
from core.models.test_result import TestResultModel as ResultModel
from core.scoring.scorer import compute_metrics


def _build_tiny_data() -> NormalizedData:
    test_cases_list = [
        CaseModel(id="TC-001", title="Login happy path", priority="P1", component="auth"),
        CaseModel(id="TC-002", title="Checkout happy path", priority="P1", component="payments"),
        CaseModel(id="TC-003", title="Refund intent", priority="P2", component="support"),
    ]
    test_cases = {tc.id: tc for tc in test_cases_list}

    results = [
        ResultModel(id="TC-001", status="passed", duration_sec=1.23, raw_name="test_login_ok"),
        ResultModel(id="TC-002", status="failed", duration_sec=4.50, raw_name="test_checkout_ok"),
        ResultModel(id="TC-003", status="skipped", duration_sec=0.00, raw_name="test_refund_intent"),
        # Unmapped
        ResultModel(id="TC-999", status="failed", duration_sec=0.50, raw_name="test_unknown"),
    ]

    return NormalizedData(test_cases=test_cases, results=results)


def test_compute_metrics_expected_counts_and_rates() -> None:
    data = _build_tiny_data()
    metrics = compute_metrics(data)

    assert metrics["total_cases"] == 3
    assert metrics["total_results"] == 4
    assert metrics["mapped_results"] == 3
    assert metrics["unmapped_results"] == 1

    assert metrics["passed"] == 1
    assert metrics["failed"] == 1
    assert metrics["skipped"] == 1

    assert metrics["failure_rate"] == pytest.approx(1 / 3)
    assert metrics["skip_rate"] == pytest.approx(1 / 3)


