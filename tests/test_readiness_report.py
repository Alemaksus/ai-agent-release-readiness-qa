from __future__ import annotations

from core.models.readiness import ReleaseRecommendation, RiskLevel, build_readiness_report, classify_risk


def test_classify_risk_high_when_failure_rate_ge_0_2() -> None:
    metrics = {
        "total_cases": 3,
        "total_results": 4,
        "mapped_results": 3,
        "unmapped_results": 1,
        "passed": 1,
        "failed": 1,
        "skipped": 1,
        "failure_rate": 1 / 3,
        "skip_rate": 1 / 3,
    }

    score = 50  # score is not the driver for HIGH in this scenario
    risk = classify_risk(score, metrics)
    assert risk == RiskLevel.HIGH


def test_build_readiness_report_recommendation_and_score_bounds() -> None:
    metrics = {
        "total_cases": 3,
        "total_results": 4,
        "mapped_results": 3,
        "unmapped_results": 1,
        "passed": 1,
        "failed": 1,
        "skipped": 1,
        "failure_rate": 1 / 3,
        "skip_rate": 1 / 3,
    }

    report = build_readiness_report(metrics)

    assert report.score.risk_level == RiskLevel.HIGH
    assert report.score.recommendation == ReleaseRecommendation.REJECT
    assert 0 <= report.score.overall_score <= 100


