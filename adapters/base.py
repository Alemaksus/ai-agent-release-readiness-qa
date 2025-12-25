"""Base adapter interface for signal extraction."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.models.signals import Signal
from core.models.test_results import TestResults


class BaseAdapter(ABC):
    """Abstract adapter contract."""

    @abstractmethod
    def extract_signals(
        self,
        test_results: TestResults,
        optional_artifacts: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        """Extract signals from provided artifacts."""

    @abstractmethod
    def get_name(self) -> str:
        """Return adapter name."""

"""Base adapter interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.models.signals import Signal
from core.models.test_results import TestResults


class BaseAdapter(ABC):
    """Base interface for adapters that extract signals from test results."""

    @abstractmethod
    def extract_signals(
        self,
        test_results: TestResults,
        optional_artifacts: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        """Extract signals from test results and optional artifacts.

        Args:
            test_results: Standardized test results
            optional_artifacts: Optional domain-specific artifacts (e.g., conversation logs)

        Returns:
            List of extracted signals
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get adapter name.

        Returns:
            Adapter name
        """
        pass

