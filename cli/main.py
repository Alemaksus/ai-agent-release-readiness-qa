from __future__ import annotations

import argparse

from cli._pipeline import run_demo, run_from_files


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="ai-agent-release-readiness-qa",
        description="Deterministic release readiness score + markdown report (no LLM).",
    )
    p.add_argument(
        "--out",
        default="reports/report.md",
        help="Output markdown report path (default: reports/report.md)",
    )
    p.add_argument(
        "--demo",
        action="store_true",
        help="Run with built-in demo data (no input files).",
    )
    p.add_argument("--junit", default=None, help="Path to JUnit XML.")
    p.add_argument("--cases", default=None, help="Path to test cases CSV.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.demo:
        saved = run_demo(args.out)
        print(f"OK: saved report to {saved}")
        return 0

    if (args.cases is None) != (args.junit is None):
        raise SystemExit("--cases and --junit must be provided together (or use --demo).")

    if args.cases is None or args.junit is None:
        raise SystemExit(
            "No input mode selected. Use either:\n"
            "  python -m cli.main --demo --out reports/report.md\n"
            "or:\n"
            "  python -m cli.main --cases <path> --junit <path> --out reports/report.md"
        )

    saved = run_from_files(cases_path=args.cases, junit_path=args.junit, out_path=args.out)
    print(f"OK: saved report to {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
