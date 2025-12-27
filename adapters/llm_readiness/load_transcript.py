from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from adapters.llm_readiness.models import Transcript, TranscriptTurn


def load_transcript(path: str) -> Transcript:
    """
    Load a transcript from JSON.

    Expected JSON shape:
      {
        "turns": [
          {
            "user_text": "...",
            "assistant_text": "...",
            "assistant_label": "optional_label",
            "expected_schema_valid": true|false,
            "refusal": true|false,
            "tool_calls": [ {"name": "...", "status": "ok"|"error"} ]
          }
        ]
      }
    """
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))

    if not isinstance(raw, dict):
        raise ValueError("Transcript JSON must be an object")
    turns_raw = raw.get("turns")
    if not isinstance(turns_raw, list):
        raise ValueError("Transcript JSON must contain 'turns' as a list")

    turns: list[TranscriptTurn] = []
    for item in turns_raw:
        if not isinstance(item, dict):
            # keep deterministic: represent invalid turn with all fields missing
            turns.append(
                TranscriptTurn(
                    user_text=None,
                    assistant_text=None,
                    assistant_label=None,
                    expected_schema_valid=None,
                    refusal=None,
                    tool_calls=None,
                )
            )
            continue

        turns.append(_turn_from_dict(item))

    return Transcript(turns=turns, source_path=str(p))


def _turn_from_dict(d: dict[str, Any]) -> TranscriptTurn:
    def _get_str(key: str) -> str | None:
        v = d.get(key)
        if v is None:
            return None
        return str(v)

    def _get_bool(key: str) -> bool | None:
        v = d.get(key)
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        # if provided but not boolean, treat as missing for deterministic "missing fields" counting
        return None

    tool_calls = d.get("tool_calls")
    if tool_calls is not None and not isinstance(tool_calls, list):
        tool_calls = None

    return TranscriptTurn(
        user_text=_get_str("user_text"),
        assistant_text=_get_str("assistant_text"),
        assistant_label=_get_str("assistant_label"),
        expected_schema_valid=_get_bool("expected_schema_valid"),
        refusal=_get_bool("refusal"),
        tool_calls=tool_calls,  # list[dict] or None
    )


