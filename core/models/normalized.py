from __future__ import annotations

from dataclasses import dataclass

from core.models.test_case import TestCaseModel
from core.models.test_result import TestResultModel


@dataclass(frozen=True, slots=True)
class NormalizedData:
    test_cases: dict[str, TestCaseModel]
    results: list[TestResultModel]


