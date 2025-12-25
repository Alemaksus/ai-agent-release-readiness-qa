from __future__ import annotations

from pathlib import Path


def save_markdown_report(path: str, content: str) -> None:
    """
    Save Markdown content to an explicit file path, creating parent dirs if needed.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


