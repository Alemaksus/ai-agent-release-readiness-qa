from __future__ import annotations

from pathlib import Path

from cli._pipeline import run_demo


def main() -> None:
    out_path = Path("reports") / "smoke_report.md"
    saved = run_demo(out_path)
    print(f"OK: saved smoke report to {saved.resolve()}")


if __name__ == "__main__":
    main()
