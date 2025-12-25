from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestCaseModel:
    id: str
    title: str
    priority: str | None = None
    component: str | None = None
    description: str | None = None


