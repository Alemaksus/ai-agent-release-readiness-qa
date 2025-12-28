from __future__ import annotations

from adapters.llm_readiness.models import AiSignal


def signals_to_markdown(signals: list[AiSignal]) -> str:
    lines: list[str] = []
    for s in signals:
        sev = s.severity.upper()
        lines.append(f"- **{sev}** {s.title}")
        for k, v in s.evidence.items():
            lines.append(f"  - {k}: {v}")
    return "\n".join(lines) + ("\n" if lines else "")



