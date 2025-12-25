"""Signal abstractions used by scoring."""

from __future__ import annotations
from enum import Enum
from typing import Any, Optional


class SignalType(str, Enum):
    """Categories of signals considered by the readiness engine."""

    STABILITY = "stability"
    REGRESSION = "regression"
    COVERAGE = "coverage"


class Signal:
    """Generic signal placeholder."""

    def __init__(
        self,
        signal_type: SignalType,
        name: str,
        value: float,
        description: str,
        evidence: list[str],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.signal_type = signal_type
        self.name = name
        self.value = value
        self.description = description
        self.evidence = evidence
        self.metadata = metadata or {}


class StabilitySignal(Signal):
    """Stability-related signal placeholder."""

    pass


class RegressionSignal(Signal):
    """Regression-related signal placeholder."""

    pass

"""Signal data structures."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class SignalType(str, Enum):
    """Type of signal."""

    STABILITY = "stability"
    REGRESSION = "regression"
    COVERAGE = "coverage"


@dataclass
class Signal:
    """Generic signal extracted from test results or artifacts."""

    signal_type: SignalType
    name: str
    value: float
    description: str
    evidence: list[str]  # Traceable evidence items
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self):
        """Validate signal."""
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.description:
            raise ValueError("description cannot be empty")
        if not self.evidence:
            raise ValueError("evidence cannot be empty")


@dataclass
class StabilitySignal(Signal):
    """Stability-related signal."""

    def __post_init__(self):
        """Validate and set signal type."""
        super().__post_init__()
        self.signal_type = SignalType.STABILITY


@dataclass
class RegressionSignal(Signal):
    """Regression-related signal."""

    def __post_init__(self):
        """Validate and set signal type."""
        super().__post_init__()
        self.signal_type = SignalType.REGRESSION

