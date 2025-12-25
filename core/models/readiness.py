"""Deterministic readiness score models and core scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class RiskLevel(str, Enum):
    """Release risk level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReleaseRecommendation(str, Enum):
    """Release recommendation."""

    APPROVE = "approve"
    CONDITIONAL = "conditional"
    REJECT = "reject"


@dataclass
class ReadinessScore:
    """Readiness score with breakdown."""

    overall_score: float  # 0-100
    stability_score: float  # 0-100
    regression_score: float  # 0-100
    coverage_score: float  # 0-100
    risk_level: RiskLevel
    recommendation: ReleaseRecommendation

    def __post_init__(self):
        """Validate readiness score."""
        if not (0 <= self.overall_score <= 100):
            raise ValueError("overall_score must be between 0 and 100")
        if not (0 <= self.stability_score <= 100):
            raise ValueError("stability_score must be between 0 and 100")
        if not (0 <= self.regression_score <= 100):
            raise ValueError("regression_score must be between 0 and 100")
        if not (0 <= self.coverage_score <= 100):
            raise ValueError("coverage_score must be between 0 and 100")


@dataclass
class BehavioralRisk:
    """A behavioral risk identified during assessment."""

    description: str
    severity: RiskLevel
    evidence: List[str]  # Traceable evidence items
    affected_tests: Optional[List[str]] = None

    def __post_init__(self):
        """Validate behavioral risk."""
        if not self.description:
            raise ValueError("description cannot be empty")
        if not self.evidence:
            raise ValueError("evidence cannot be empty")


@dataclass
class ReadinessReport:
    """Complete readiness assessment report."""

    score: ReadinessScore
    risks: List[BehavioralRisk]
    data_availability: dict[str, bool]  # What data was available
    assumptions: List[str]  # Explicit assumptions made
    signal_summary: dict[str, int]  # Count of signals by type
    metrics: dict  # Deterministic computed metrics used for scoring/reporting

    def __post_init__(self):
        """Validate readiness report."""
        if not self.assumptions:
            raise ValueError("assumptions cannot be empty - must state data availability")


def compute_release_readiness_score(metrics: dict) -> int:
    """
    Compute a deterministic release readiness score (0..100).

    Explainable penalty model:
    - failure_rate penalty: 1 point per 1% failed (capped at 70)
    - skip_rate penalty: 0.5 points per 1% skipped (capped at 20)
    - unmapped_rate penalty: 0.5 points per 1% unmapped (capped at 20)
    where unmapped_rate = unmapped_results / total_results (0 if total_results==0)
    """
    failure_rate = float(metrics.get("failure_rate", 0.0) or 0.0)
    skip_rate = float(metrics.get("skip_rate", 0.0) or 0.0)
    total_results = int(metrics.get("total_results", 0) or 0)
    unmapped_results = int(metrics.get("unmapped_results", 0) or 0)

    unmapped_rate = (unmapped_results / total_results) if total_results > 0 else 0.0

    failure_penalty = min(70, int(round(failure_rate * 100)))
    skip_penalty = min(20, int(round(skip_rate * 50)))
    unmapped_penalty = min(20, int(round(unmapped_rate * 50)))

    score = 100 - failure_penalty - skip_penalty - unmapped_penalty
    if score < 0:
        score = 0
    if score > 100:
        score = 100
    return int(score)


def classify_risk(score: int, metrics: dict) -> RiskLevel:
    """
    Classify risk using score thresholds with simple metric-based escalations.
    """
    failure_rate = float(metrics.get("failure_rate", 0.0) or 0.0)
    skip_rate = float(metrics.get("skip_rate", 0.0) or 0.0)
    total_results = int(metrics.get("total_results", 0) or 0)
    unmapped_results = int(metrics.get("unmapped_results", 0) or 0)
    unmapped_rate = (unmapped_results / total_results) if total_results > 0 else 0.0

    # Escalate to HIGH if major execution/traceability issues are present.
    if failure_rate >= 0.2 or unmapped_rate >= 0.3:
        return RiskLevel.HIGH

    # Escalate LOW->MEDIUM if significant skipping is present.
    if score >= 85 and (skip_rate > 0.1 or unmapped_rate > 0.05):
        return RiskLevel.MEDIUM

    if score >= 85:
        return RiskLevel.LOW
    if score >= 70:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH


def build_readiness_report(metrics: dict) -> ReadinessReport:
    """
    Build a minimal deterministic readiness report from computed metrics.
    """
    score_int = compute_release_readiness_score(metrics)
    risk_level = classify_risk(score_int, metrics)

    if risk_level == RiskLevel.LOW:
        recommendation = ReleaseRecommendation.APPROVE
    elif risk_level == RiskLevel.MEDIUM:
        recommendation = ReleaseRecommendation.CONDITIONAL
    else:
        recommendation = ReleaseRecommendation.REJECT

    readiness_score = ReadinessScore(
        overall_score=float(score_int),
        stability_score=float(score_int),
        regression_score=float(score_int),
        coverage_score=float(score_int),
        risk_level=risk_level,
        recommendation=recommendation,
    )

    risks: list[BehavioralRisk] = []
    failed = int(metrics.get("failed", 0) or 0)
    skipped = int(metrics.get("skipped", 0) or 0)
    unmapped = int(metrics.get("unmapped_results", 0) or 0)
    failure_rate = float(metrics.get("failure_rate", 0.0) or 0.0)
    skip_rate = float(metrics.get("skip_rate", 0.0) or 0.0)

    if failed > 0:
        risks.append(
            BehavioralRisk(
                description="Test failures detected in mapped results",
                severity=RiskLevel.HIGH if failure_rate >= 0.1 else RiskLevel.MEDIUM,
                evidence=[f"failed={failed}", f"failure_rate={failure_rate:.3f}"],
                affected_tests=None,
            )
        )
    if skip_rate > 0.2 or skipped > 0:
        risks.append(
            BehavioralRisk(
                description="Skipped tests reduce confidence in coverage",
                severity=RiskLevel.MEDIUM if skip_rate <= 0.2 else RiskLevel.HIGH,
                evidence=[f"skipped={skipped}", f"skip_rate={skip_rate:.3f}"],
                affected_tests=None,
            )
        )
    if unmapped > 0:
        risks.append(
            BehavioralRisk(
                description="Unmapped results indicate traceability gaps",
                severity=RiskLevel.MEDIUM,
                evidence=[f"unmapped_results={unmapped}", f"total_results={int(metrics.get('total_results', 0) or 0)}"],
                affected_tests=None,
            )
        )

    data_availability = {
        "metrics": True,
        "test_results_present": int(metrics.get("total_results", 0) or 0) > 0,
        "test_cases_present": int(metrics.get("total_cases", 0) or 0) > 0,
    }

    assumptions = [
        "Score/risk computed deterministically from current-run test metrics only (no LLM judging, no trend/history inputs)."
    ]

    signal_summary = {
        "failed": failed,
        "skipped": skipped,
        "unmapped_results": unmapped,
    }

    return ReadinessReport(
        score=readiness_score,
        risks=risks,
        data_availability=data_availability,
        assumptions=assumptions,
        signal_summary=signal_summary,
        metrics=dict(metrics),
    )

