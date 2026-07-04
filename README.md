# AegisLegacy

**Python/Perl Runtime Security & Modernization Platform** — a platform for
scanning, scoring, and planning the modernization of legacy Perl and
Python applications.

> Status: in active, incremental development. See [ROADMAP.md](ROADMAP.md)
> for exactly what is implemented vs. planned — this README describes the
> target shape of the project, not a finished product.

## What it does (target scope)

AegisLegacy scans a legacy codebase (`.pl`, `.pm`, `.cgi`, `.py`, `.sh`,
config files) and reports on:

- command injection risk (`system()`, backticks, `subprocess(shell=True)`)
- unsafe dynamic code execution (`eval`, `exec`, insecure deserialization)
- hardcoded secrets and cloud credentials
- legacy/hard-to-maintain patterns (two-argument `open`, oversized
  functions, missing input validation)

...then turns the findings into a **security score** (0–100, with an
Excellent/Good/Needs improvement/Risky/Critical classification), an HTML
report, and modernization recommendations (keep / refactor / isolate /
migrate / replace).

## Architecture

```mermaid
flowchart LR
    subgraph Inputs
        A[Perl / Python legacy tree]
    end
    subgraph Engine
        R[rules/*.yaml] --> L[RuleLoader]
        L --> E[RuleEngine]
        A --> E
        E --> F[Findings]
        F --> S[Scoring service]
    end
    subgraph Consumers
        CLI[CLI - Typer - implemented]
        API[Backend API - FastAPI]
        Agent[Perl agent]
        Report[HTML report]
    end
    E --> CLI
    E --> API
    Agent -. JSON .-> API
    S --> Report
    F --> Report
```

Layering (implemented so far in `backend/app`):

- `domain/` — pure data models (`Severity`, `Language`, `Finding`). No I/O.
- `rules/` — YAML schema validation (`schema.py`), loading (`loader.py`),
  and pattern matching against files (`engine.py`).
- `services/` — orchestration on top of domain objects (`scoring.py`).
- `api/`, `repositories/`, `workers/`, `reports/`, `security/`,
  `observability/` — not implemented yet; see `ROADMAP.md`.

## What's actually implemented right now

**The rules engine** — the dependency root for everything else:

- `backend/app/domain/{severity,language,findings}.py`
- `backend/app/rules/{schema,loader,engine}.py`
- `backend/app/services/scoring.py`
- 8 demo detection rules in `rules/{perl,python,secrets}/`
- 50 passing tests (`backend/tests/`), `ruff check` clean, `mypy --strict` clean

**The CLI**, built directly on top of it:

- `aegis scan <path>` — scans a file or directory, prints a Rich findings
  table and a score panel, optionally writes JSON (`--output`), exits
  non-zero on critical findings.
- `aegis rules list` — lists every loaded detection rule.
- `aegis doctor` — checks the local environment (Python version, rules
  directory present and loading correctly).
- 21 passing tests (`cli/tests/`), `ruff check` clean, `mypy --strict` clean.
- `report generate`, `score <scan_id>` and `diff` are intentionally **not**
  registered yet — they need scan persistence (backend API), see
  `ROADMAP.md`.

### Try it

```bash
# from the repo root, one shared virtualenv for backend + cli
python -m venv .venv
.venv/Scripts/activate          # or: source .venv/bin/activate
pip install -e "backend[dev,api]" -e "cli[dev]"

pytest backend/tests cli/tests   # 71 passed
ruff check backend cli           # clean
mypy backend/app                 # clean, strict mode
mypy --config-file cli/pyproject.toml cli/aegislegacy  # clean, strict mode

aegis rules list
aegis scan ./rules               # try it on any path; demo-legacy-app is not built yet
```

```python
from pathlib import Path
from app.rules.loader import load_rules_from_directory
from app.rules.engine import RuleEngine
from app.services.scoring import compute_score

rules = load_rules_from_directory(Path("rules"))
engine = RuleEngine(rules)
findings = engine.scan_tree(Path("/path/to/legacy/project"))

result = compute_score(findings)
print(result.score, result.classification)
```

## Stack

- **Python**: 3.12+, pydantic v2, Typer, Rich, pytest, ruff, mypy (strict)
  — implemented (rules engine + CLI).
- **Perl 5**, **FastAPI**, **SQLModel**, **Jinja2** — planned, see
  `ROADMAP.md`.

## Why this project

It's built module-by-module, in dependency order, with each module held to
the same bar before moving to the next: typed, tested, linted, and
documented — rather than a wide surface of half-working scaffolding. The
rules engine shipped first because the CLI, the API, and the Perl agent's
JSON contract all depend on its `Finding` shape; the CLI shipped second
because it validates that shape end-to-end with zero extra infrastructure.

## Security note

This is a defensive tool. Any intentionally vulnerable code lives only
under `demo-legacy-app/` (not yet added) as inert, local-only fixtures for
detection demos — never real secrets, never offensive tooling.

## License

BSD 3-Clause, see [LICENSE](LICENSE).
