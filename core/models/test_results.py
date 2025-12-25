"""Placeholders for test result data structures."""

from enum import Enum
from typing import List, Optional


class TestStatus(str, Enum):
    """Execution status for a single test case."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestResult:
    """Represents a single test case result."""

    def __init__(
        self,
        test_id: str,
        status: TestStatus,
        duration_ms: int,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        self.test_id = test_id
        self.status = status
        self.duration_ms = duration_ms
        self.error_message = error_message
        self.metadata = metadata or {}


class TestRun:
    """Represents one execution run containing multiple test results."""

    def __init__(
        self,
        run_id: str,
        timestamp: str,
        results: List[TestResult],
        metadata: Optional[dict] = None,
    ) -> None:
        self.run_id = run_id
        self.timestamp = timestamp
        self.results = results
        self.metadata = metadata or {}


class TestResults:
    """Collection of test runs for analysis."""

    def __init__(self, test_runs: List[TestRun]) -> None:
        self.test_runs = test_runs

"""Test result data structures."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TestStatus(str, Enum):
    """Test execution status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result."""

    test_id: str
    status: TestStatus
    duration_ms: int
    error_message: Optional[str] = None
    metadata: Optional[dict] = None

    def __post_init__(self):
        """Validate test result."""
        if self.duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        if not self.test_id:
            raise ValueError("test_id cannot be empty")


@dataclass
class TestRun:
    """A single test run containing multiple test results."""

    run_id: str
    timestamp: datetime
    results: List[TestResult]
    metadata: Optional[dict] = None

    def __post_init__(self):
        """Validate test run."""
        if not self.run_id:
            raise ValueError("run_id cannot be empty")
        if not self.results:
            raise ValueError("results cannot be empty")

    @property
    def total_tests(self) -> int:
        """Total number of tests in this run."""
        return len(self.results)

    @property
    def passed_count(self) -> int:
        """Number of passed tests."""
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)

    @property
    def failed_count(self) -> int:
        """Number of failed tests."""
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)

    @property
    def pass_rate(self) -> float:
        """Pass rate as a fraction (0.0 to 1.0)."""
        if self.total_tests == 0:
            return 0.0
        return self.passed_count / self.total_tests


@dataclass
class TestResults:
    """Collection of test runs."""

    test_runs: List[TestRun]

    def __post_init__(self):
        """Validate test results."""
        if not self.test_runs:
            raise ValueError("test_runs cannot be empty")

    @property
    def total_runs(self) -> int:
        """Total number of test runs."""
        return len(self.test_runs)

    @property
    def unique_test_ids(self) -> set[str]:
        """Set of all unique test IDs across all runs."""
        test_ids = set()
        for run in self.test_runs:
            test_ids.update(r.test_id for r in run.results)
        return test_ids

    def get_test_history(self, test_id: str) -> List[TestResult]:
        """Get execution history for a specific test ID."""
        history = []
        for run in self.test_runs:
            for result in run.results:
                if result.test_id == test_id:
                    history.append(result)
        return history

