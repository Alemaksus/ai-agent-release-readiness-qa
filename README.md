# AI Agent Release Readiness QA (deterministic)

## What it does

- Computes **deterministic QA metrics** from test cases + test results (no LLM required).
- Produces a **readiness score (0–100)**, **risk level**, and **release recommendation**.
- Renders a **Markdown report** and saves it to a path you choose.

## Inputs

- **CSV test cases**: see `samples/test_cases.csv`
- **JUnit XML results**: see `samples/junit.xml`
- **Optional AI/LLM transcript (JSON)**: see `samples/llm_transcript.json` (keys per turn: `user_text`, `assistant_text`, optional `assistant_label`, `expected_schema_valid`, `refusal`, `tool_calls`)

## Outputs

- **Score / risk / recommendation** (derived deterministically from current-run metrics)
- **Markdown report** written to `--out`

## Quickstart

### Windows (PowerShell) — Quickstart

```powershell
cd C:\path\to\ai-agent-release-readiness-qa
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
pytest
python -m cli.main --demo --out reports\report.md
```

### macOS/Linux (bash) — Quickstart

```bash
cd /path/to/ai-agent-release-readiness-qa
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
pytest
python -m cli.main --demo --out reports/report.md
```

## Run with files (CSV + JUnit)

The `samples/` folder contains runnable inputs.

### Windows (PowerShell) — File mode

```powershell
python -m cli.main --cases samples\test_cases.csv --junit samples\junit.xml --out reports\from_files.md
```

### macOS/Linux (bash) — File mode

```bash
python -m cli.main --cases samples/test_cases.csv --junit samples/junit.xml --out reports/from_files.md
```

## Optional AI/LLM transcript signals

```powershell
python -m cli.main --demo --transcript samples\llm_transcript.json --out reports\with_ai.md
```

```powershell
python -m cli.main --demo --transcript samples\llm_transcript.json --baseline-transcript samples\llm_transcript_baseline.json --out reports\with_ai_drift.md
```

See `docs/ai-semantics.md` for the advisory semantics and drift interpretation policy.

## Notes / limitations

- **Deterministic only**: no LLM judging, no network calls.
- **Current-run only**: score is computed from the provided results (no trend/history analysis).

## Intended audience

- QA engineers validating AI-powered systems
- Teams shipping agentic workflows or chat-based products
- Founders and PMs needing a deterministic pre-release signal.