"""Generic signal extraction from basic test results (skeleton)."""

from typing import Any, Dict, List, Optional

from adapters.base import BaseAdapter
from core.models.signals import Signal
from core.models.test_results import TestResults


class GenericAdapter(BaseAdapter):
    """Extracts baseline signals without AI artifacts."""

    def extract_signals(
        self,
        test_results: TestResults,
        optional_artifacts: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        """Extract generic signals from test results."""
        raise NotImplementedError("Generic signal extraction will be implemented later.")

    def get_name(self) -> str:
        """Return adapter name."""
        return "generic"

"""Generic adapter for extracting basic signals from test results."""

from typing import Any, Dict, List, Optional

from adapters.base import BaseAdapter
from core.models.readiness import BehavioralRisk, RiskLevel
from core.models.signals import RegressionSignal, SignalType, StabilitySignal
from core.models.test_results import TestResults
from core.scoring.regression import (
    calculate_failure_rate_trend,
    identify_new_failures,
)
from core.scoring.stability import (
    calculate_pass_rate_consistency,
    detect_flaky_tests,
)


class GenericAdapter(BaseAdapter):
    """Generic adapter that works with only basic test results."""

    def extract_signals(
        self,
        test_results: TestResults,
        optional_artifacts: Optional[Dict[str, Any]] = None,
    ) -> List[StabilitySignal | RegressionSignal]:
        """Extract generic signals from test results.

        Args:
            test_results: Standardized test results
            optional_artifacts: Ignored (not used by generic adapter)

        Returns:
            List of extracted signals
        """
        signals: List[StabilitySignal | RegressionSignal] = []

        # Stability signals
        pass_rate_consistency = calculate_pass_rate_consistency(test_results)
        flaky_tests = detect_flaky_tests(test_results)
        flakiness_rate = (
            len(flaky_tests) / len(test_results.unique_test_ids)
            if test_results.unique_test_ids
            else 0.0
        )

        # Calculate average pass rate across all runs
        avg_pass_rate = (
            sum(run.pass_rate for run in test_results.test_runs)
            / test_results.total_runs
            if test_results.total_runs > 0
            else 0.0
        )

        # Pass rate consistency signal
        signals.append(
            StabilitySignal(
                signal_type=SignalType.STABILITY,
                name="pass_rate_consistency",
                value=pass_rate_consistency * 100.0,
                description=f"Consistency of pass rates across {test_results.total_runs} runs",
                evidence=[
                    f"Pass rate consistency: {pass_rate_consistency:.2%}",
                    f"Average pass rate: {avg_pass_rate:.2%}",
                ],
                metadata={"consistency": pass_rate_consistency, "avg_pass_rate": avg_pass_rate},
            )
        )

        # Flakiness signal
        signals.append(
            StabilitySignal(
                signal_type=SignalType.STABILITY,
                name="test_flakiness",
                value=(1.0 - flakiness_rate) * 100.0,
                description=f"Test flakiness rate: {len(flaky_tests)} flaky test(s) out of {len(test_results.unique_test_ids)} total",
                evidence=[
                    f"Flaky tests detected: {len(flaky_tests)}",
                    f"Flakiness rate: {flakiness_rate:.2%}",
                ]
                + ([f"Flaky test IDs: {', '.join(flaky_tests)}"] if flaky_tests else []),
                metadata={"flaky_tests": flaky_tests, "flakiness_rate": flakiness_rate},
            )
        )

        # Regression signals
        failure_rate_trend = calculate_failure_rate_trend(test_results)
        new_failures = identify_new_failures(test_results)
        total_tests = len(test_results.unique_test_ids)
        current_failure_rate = (
            sum(run.failed_count for run in test_results.test_runs[-3:])
            / sum(run.total_tests for run in test_results.test_runs[-3:])
            if test_results.test_runs
            else 0.0
        )

        # Failure rate trend signal
        signals.append(
            RegressionSignal(
                signal_type=SignalType.REGRESSION,
                name="failure_rate_trend",
                value=((failure_rate_trend + 1.0) / 2.0) * 100.0,
                description=f"Trend in failure rate across {test_results.total_runs} runs",
                evidence=[
                    f"Failure rate trend: {failure_rate_trend:.2f} ({'improving' if failure_rate_trend > 0 else 'worsening' if failure_rate_trend < 0 else 'stable'})",
                    f"Current failure rate: {current_failure_rate:.2%}",
                ],
                metadata={"trend": failure_rate_trend, "current_failure_rate": current_failure_rate},
            )
        )

        # New failures signal
        signals.append(
            RegressionSignal(
                signal_type=SignalType.REGRESSION,
                name="new_failures",
                value=max(0.0, 100.0 - (len(new_failures) / total_tests * 100.0) if total_tests > 0 else 100.0),
                description=f"New failures detected: {len(new_failures)} test(s)",
                evidence=(
                    [f"New failures: {len(new_failures)}"]
                    + ([f"New failure test IDs: {', '.join(new_failures)}"] if new_failures else [])
                ),
                metadata={"new_failures": new_failures, "total_tests": total_tests},
            )
        )

        return signals

    def get_name(self) -> str:
        """Get adapter name.

        Returns:
            Adapter name
        """
        return "generic"

