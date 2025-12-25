"""Readiness score and reporting placeholders."""

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


class ReadinessScore:
    """Aggregated readiness score with components."""

    def __init__(
        self,
        overall_score: float,
        stability_score: float,
        regression_score: float,
        coverage_score: float,
        risk_level: RiskLevel,
        recommendation: ReleaseRecommendation,
    ) -> None:
        self.overall_score = overall_score
        self.stability_score = stability_score
        self.regression_score = regression_score
        self.coverage_score = coverage_score
        self.risk_level = risk_level
        self.recommendation = recommendation


class BehavioralRisk:
    """Represents a behavioral risk identified during assessment."""

    def __init__(
        self,
        description: str,
        severity: RiskLevel,
        evidence: List[str],
        affected_tests: Optional[List[str]] = None,
    ) -> None:
        self.description = description
        self.severity = severity
        self.evidence = evidence
        self.affected_tests = affected_tests or []


class ReadinessReport:
    """Full readiness assessment report placeholder."""

    def __init__(
        self,
        score: ReadinessScore,
        risks: List[BehavioralRisk],
        data_availability: dict,
        assumptions: List[str],
        signal_summary: dict,
    ) -> None:
        self.score = score
        self.risks = risks
        self.data_availability = data_availability
        self.assumptions = assumptions
        self.signal_summary = signal_summary

"""Readiness score models."""

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

    def __post_init__(self):
        """Validate readiness report."""
        if not self.assumptions:
            raise ValueError("assumptions cannot be empty - must state data availability")

