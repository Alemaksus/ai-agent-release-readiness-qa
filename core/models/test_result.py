from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestResultModel:
    id: str
    status: str
    duration_sec: float | None = None
    raw_name: str | None = None


