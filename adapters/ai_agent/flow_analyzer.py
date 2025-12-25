"""Analyzer for conversation flow artifacts (skeleton)."""

from typing import Any, Dict, List, Optional

from core.models.signals import Signal
from core.models.test_results import TestResults


class FlowAnalyzer:
    """Examines flow traces for anomalies and completion (placeholder)."""

    def analyze(
        self,
        test_results: TestResults,
        flows: Optional[List[Dict[str, Any]]],
    ) -> List[Signal]:
        """Analyze flow data and return signals."""
        raise NotImplementedError("Flow analysis will be implemented later.")

"""Analyzer for conversation flow patterns."""

from typing import Any, Dict, List, Optional

from core.models.signals import RegressionSignal, SignalType, StabilitySignal
from core.models.test_results import TestResults


class FlowAnalyzer:
    """Analyzes conversation flow patterns for behavioral issues."""

    def analyze(
        self,
        test_results: TestResults,
        flows: Optional[List[Dict[str, Any]]] = None,
    ) -> List[StabilitySignal | RegressionSignal]:
        """Analyze flow data and extract signals.

        Args:
            test_results: Test results (for context)
            flows: Optional list of conversation flow records

        Returns:
            List of signals (empty if no flows provided)
        """
        signals: List[StabilitySignal | RegressionSignal] = []

        if flows is None or len(flows) == 0:
            return signals  # Graceful degradation

        # Analyze flow completion rates
        completed_flows = sum(
            1
            for flow in flows
            if flow.get("status") == "completed"
            or flow.get("completed", False)
            or flow.get("reached_end", False)
        )
        completion_rate = completed_flows / len(flows) if flows else 0.0

        signals.append(
            StabilitySignal(
                signal_type=SignalType.STABILITY,
                name="flow_completion_rate",
                value=completion_rate * 100.0,
                description=f"Flow completion rate: {completed_flows}/{len(flows)}",
                evidence=[
                    f"Completed flows: {completed_flows}",
                    f"Total flows: {len(flows)}",
                    f"Completion rate: {completion_rate:.2%}",
                ],
                metadata={"completion_rate": completion_rate, "total": len(flows)},
            )
        )

        # Analyze flow anomalies (if step data available)
        if all("steps" in flow for flow in flows):
            anomaly_count = 0
            for flow in flows:
                steps = flow.get("steps", [])
                # Check for loops (repeated steps)
                if len(steps) > len(set(steps)):
                    anomaly_count += 1
                # Check for unexpected terminations
                if flow.get("status") != "completed" and len(steps) > 0:
                    anomaly_count += 1

            anomaly_rate = anomaly_count / len(flows) if flows else 0.0

            signals.append(
                RegressionSignal(
                    signal_type=SignalType.REGRESSION,
                    name="flow_anomalies",
                    value=(1.0 - anomaly_rate) * 100.0,
                    description=f"Flow anomalies detected: {anomaly_count}/{len(flows)}",
                    evidence=[
                        f"Anomalous flows: {anomaly_count}",
                        f"Anomaly rate: {anomaly_rate:.2%}",
                    ],
                    metadata={"anomaly_count": anomaly_count, "anomaly_rate": anomaly_rate},
                )
            )

        return signals

