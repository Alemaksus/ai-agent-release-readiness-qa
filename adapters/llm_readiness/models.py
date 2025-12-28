from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


Severity = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class TranscriptTurn:
    """
    A single user<->assistant interaction.

    Fields are intentionally permissive to allow counting missing/invalid fields deterministically.
    """

    user_text: str | None
    assistant_text: str | None
    assistant_label: str | None
    expected_schema_valid: bool | None
    refusal: bool | None
    tool_calls: list[dict[str, Any]] | None


@dataclass(frozen=True, slots=True)
class Transcript:
    turns: list[TranscriptTurn]
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class AiSignal:
    severity: Severity
    title: str
    evidence: dict[str, Any]



