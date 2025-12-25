"""AI agent adapter for extracting signals from optional AI artifacts (skeleton)."""

from typing import Any, Dict, List, Optional

from adapters.base import BaseAdapter
from adapters.ai_agent.conversation_analyzer import ConversationAnalyzer
from adapters.ai_agent.flow_analyzer import FlowAnalyzer
from adapters.ai_agent.intent_analyzer import IntentAnalyzer
from core.models.signals import Signal
from core.models.test_results import TestResults


class AIAgentAdapter(BaseAdapter):
    """Orchestrates AI-specific analyzers (placeholder)."""

    def __init__(self) -> None:
        self.conversation_analyzer = ConversationAnalyzer()
        self.intent_analyzer = IntentAnalyzer()
        self.flow_analyzer = FlowAnalyzer()

    def extract_signals(
        self,
        test_results: TestResults,
        optional_artifacts: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        """Extract signals from AI artifacts if present."""
        raise NotImplementedError("AI agent signal extraction will be implemented later.")

    def get_name(self) -> str:
        """Return adapter name."""
        return "ai_agent"

"""AI agent adapter that extracts signals from AI-specific artifacts."""

from typing import Any, Dict, List, Optional

from adapters.ai_agent.conversation_analyzer import ConversationAnalyzer
from adapters.ai_agent.flow_analyzer import FlowAnalyzer
from adapters.ai_agent.intent_analyzer import IntentAnalyzer
from adapters.base import BaseAdapter
from core.models.signals import RegressionSignal, Signal, SignalType, StabilitySignal
from core.models.test_results import TestResults


class AIAgentAdapter(BaseAdapter):
    """Adapter for AI agent-specific signal extraction."""

    def __init__(self):
        """Initialize AI agent adapter with analyzers."""
        self.conversation_analyzer = ConversationAnalyzer()
        self.intent_analyzer = IntentAnalyzer()
        self.flow_analyzer = FlowAnalyzer()

    def extract_signals(
        self,
        test_results: TestResults,
        optional_artifacts: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        """Extract AI-specific signals from test results and artifacts.

        Args:
            test_results: Standardized test results
            optional_artifacts: Optional AI artifacts (conversations, intents, flows)

        Returns:
            List of extracted signals (empty if no artifacts available)
        """
        signals: List[Signal] = []

        if optional_artifacts is None:
            optional_artifacts = {}

        # Extract conversation signals (graceful degradation)
        conversation_signals = self.conversation_analyzer.analyze(
            test_results, optional_artifacts.get("conversations")
        )
        signals.extend(conversation_signals)

        # Extract intent signals (graceful degradation)
        intent_signals = self.intent_analyzer.analyze(
            test_results, optional_artifacts.get("intents")
        )
        signals.extend(intent_signals)

        # Extract flow signals (graceful degradation)
        flow_signals = self.flow_analyzer.analyze(
            test_results, optional_artifacts.get("flows")
        )
        signals.extend(flow_signals)

        return signals

    def get_name(self) -> str:
        """Get adapter name.

        Returns:
            Adapter name
        """
        return "ai_agent"

