# AegisLegacy — Roadmap

This repository is built incrementally, in depth-first order: each module is
implemented to a real, tested, senior-quality standard before the next one
starts — no shallow scaffolding left pretending to be finished.

## Status

| Module | Status | Notes |
|---|---|---|
| Rules engine (`backend/app/rules`, `backend/app/domain`, `backend/app/services/scoring.py`) | **Done** | Schema validation, YAML loader, pattern matcher, scoring. 50 tests, ruff + mypy strict clean. |
| Demo rule set (`rules/`) | **Done** | 8 rules across Perl, Python and secrets categories. |
| CLI (`cli/`) | **Done** | Typer + Rich: `aegis scan`, `aegis rules list`, `aegis doctor`. 21 tests, ruff + mypy strict clean. `report generate`/`score <scan_id>`/`diff` need scan persistence (see below) and are intentionally not registered yet. |
| Backend API (`backend/app/api`, `core`, `repositories`) | Not started | FastAPI + SQLModel (SQLite for the core edition, no Postgres/Redis/Celery in this iteration). |
| Agent Perl (`agent-perl/`) | Not started | Independent scanner producing JSON, consumable standalone or via the API. |
| Reporting (`backend/app/reports`) | Not started | Jinja2 HTML report from scan results. |
| Demo legacy app (`demo-legacy-app/`) | Not started | Deliberately vulnerable, local-only, defensive-use fixtures. |
| Modernization Advisor (`rules/modernization`) | Not started | Heuristics mapping legacy patterns to migration recommendations. |
| CI/CD (`.github/workflows`) | Not started | |
| `.claude/` (rules, skills, hooks) | Not started | |
| Docs (`docs/`) | Not started | |

## Why this order

The rules engine is the dependency root: the CLI, the API and the Perl
agent's JSON contract all need a stable `Finding` shape and a working
`RuleEngine` before they can be built without guessing at interfaces. The
CLI came next because it validates the rules engine end-to-end against
real files with zero additional infrastructure (no DB, no HTTP).

## Known scope gaps in the CLI (by design, not oversight)

- `aegis report generate <scan_id>`, `aegis score <scan_id>` and
  `aegis diff <id1> <id2>` are not implemented: they need a `scan_id`,
  which requires the backend's persistence layer (`repositories/` +
  `api/`) to exist first. `aegis scan` already prints the score inline for
  the single-scan case in the meantime.
- The CLI depends on `app` from `../backend` as a monorepo path
  dependency (not a published package) — see the comment in
  `cli/pyproject.toml`.

## Scope decisions for this iteration ("core" edition)

To keep every shipped module fully working and testable without external
infrastructure, this iteration deliberately **does not** include:
Postgres, Redis, Celery/RQ, or a Next.js/Streamlit dashboard. The backend
API will use SQLite via SQLModel and run scans synchronously. These can be
swapped in later without changing the domain/rules layer.
