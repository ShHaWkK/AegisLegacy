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
| Backend API (`backend/app/api`, `core`, `repositories`, `services`, `security`, `observability`) | **Done** | FastAPI + SQLModel on SQLite. `POST/GET /api/v1/scans`, `/scans/{id}`, `/scans/{id}/findings`, `/scans/{id}/score`, `GET /api/v1/rules`, `GET /health`. API-key auth on the write endpoint, pagination on list, structlog JSON logging. 83 tests, ruff + mypy strict clean. |
| Agent Perl (`agent-perl/`) | **Done** | Standalone Perl 5 agent, core-modules only (no cpan install needed): `Aegis::Collector` (walk + hash + metadata), `Aegis::Scanner` (4 hardcoded high-value rules), `Aegis::Reporter` (JSON to file or HTTP POST). `bin/aegis-agent.pl` verified end-to-end against a live vulnerable fixture. 5 test files, 17 subtests, all passing (`make test-perl`, which runs each `.t` directly with `perl` rather than `prove` — see note below). |
| Reporting (`backend/app/reports`) | Not started | Jinja2 HTML report from scan results. |
| Demo legacy app (`demo-legacy-app/`) | **Done** | 6 deliberately vulnerable files (2 Perl, 2 Python, a `.env`, a config file) exercising all 8 demo rules. Only fake secrets, no offensive payloads. Verified with the CLI, the API and the Perl agent — all three agree on the findings. |
| Modernization Advisor (`rules/modernization`) | Not started | Heuristics mapping legacy patterns to migration recommendations. |
| CI/CD (`.github/workflows`) | Not started | |
| `.claude/` (rules, skills, hooks) | Not started | |
| Docs (`docs/`) | Partial | `demo-script.md` and `interview-pitch.md` done. `architecture.md`, `threat-model.md`, `security-model.md`, `rules-engine.md`, `modernization-strategy.md`, `ci-cd.md` not started. |

## Why this order

The rules engine is the dependency root: the CLI, the API and the Perl
agent's JSON contract all need a stable `Finding` shape and a working
`RuleEngine` before they can be built without guessing at interfaces. The
CLI came next because it validates the rules engine end-to-end against
real files with zero additional infrastructure (no DB, no HTTP).

## Known scope gaps (by design, not oversight)

- `aegis report generate <scan_id>`, `aegis score <scan_id>` and
  `aegis diff <id1> <id2>` are still not registered in the CLI. The
  backend now has the persistence layer they'd need (`GET /scans/{id}`,
  `/score`), so wiring the CLI to call the API over HTTP is the natural
  next step — not done yet because it wasn't asked for in this iteration.
  `aegis scan` already prints the score inline for the single-scan case.
- The CLI depends on `app` from `../backend` as a monorepo path
  dependency (not a published package) — see the comment in
  `cli/pyproject.toml`.
- `GET /api/v1/scans/{scan_id}/report` (HTML report) is not implemented:
  it needs the `backend/app/reports` module (Jinja2 templates), which
  hasn't been built yet.
- Scans run **synchronously inside the HTTP request** — acceptable for the
  directory sizes a demo/portfolio target has, but would need a worker
  queue (Celery/RQ) for large trees or concurrent scans in production.
- No Alembic migrations: `SQLModel.metadata.create_all()` runs at startup.
  Fine pre-production with one table family; the natural upgrade path is
  documented in `backend/app/repositories/database.py`.
- `load_rules_from_directory` re-parses every YAML file and recompiles
  every regex on **every** call — `GET /rules` and `POST /scans` both pay
  this cost per request, with no caching. Fine at 8 demo rules; would need
  an `lru_cache` keyed on `rules_dir` (with explicit invalidation) before
  this matters at a larger rule-set scale.
- Domain exceptions (`ScanTargetNotFoundError`, `RuleLoadError`) are mapped
  to HTTP status codes by hand in each route (`backend/app/api/routes/`)
  rather than through a central FastAPI `exception_handler`. Acceptable at
  2 routes and 2 exception types; revisit when `reports/` adds its own
  exception type so the mapping doesn't get copy-pasted a third time.
- `RuleEngine.IGNORED_DIRECTORIES` (`.git`, `node_modules`, `venv`, ...) is
  a hardcoded set in `backend/app/rules/engine.py`, not configurable per
  scan or per project (e.g. no way to also skip a vendored `vendor/`).
- `ScoreResult.findings_by_severity` (the per-severity breakdown the CLI
  displays) is computed at scan time but not persisted — `ScanRecord` only
  stores the final score/classification/count. `GET /scans/{id}/score`
  can't expose the breakdown for a past scan; only `aegis scan`'s
  in-process output has it.
- The 8 demo rules use single-line regexes; they can't reliably match
  patterns split across a function-call's arguments beyond simple nesting
  (e.g. `subprocess-shell` handles one level of nested parens,
  `insecure-deserialization`'s `yaml.load` check only looks 80 characters
  ahead for `Loader=yaml.SafeLoader`). This is an inherent limit of
  regex-based detection, not a bug to "finish" — an AST-based scanner would
  be the next tier of accuracy, out of scope for the core edition.
- `prove` (the standard Perl test runner) is broken on the Cygwin Perl
  used to build this repo — it's missing `TAP::Harness::Env`, a module
  that isn't part of a minimal Cygwin Perl install. `make test-perl` works
  around this by running each `t/*.t` file directly with `perl`, which
  needs no extra module. On a Perl install with a working `prove`, `prove
  -l agent-perl/t` works too.
- Portability note (already fixed, kept for context): `Aegis::Collector`
  used to hand a relative path straight to `File::Find::find`, which
  silently found zero files on this repo's Cygwin Perl when given a
  relative `--path`. It now resolves the path with `Cwd::abs_path` first.
  Caught by actually running the agent against `demo-legacy-app` with a
  relative path — the unit tests alone hadn't caught it, since
  `File::Temp::tempdir()` always returns an absolute path. A regression
  test now covers the relative-path case explicitly (`t/collector.t`).
- The Perl agent's `--api` flag POSTs its own self-contained JSON report
  to a URL as-is. It does not (yet) match the backend's `POST
  /api/v1/scans` contract, which expects `{"target_path": "..."}` and runs
  the scan itself in Python — there's no endpoint today for ingesting
  pre-computed findings from the Perl agent. See `agent-perl/README.md`.

## Scope decisions for this iteration ("core" edition)

To keep every shipped module fully working and testable without external
infrastructure, this iteration deliberately **does not** include:
Postgres, Redis, Celery/RQ, or a Next.js/Streamlit dashboard. The backend
API uses SQLite via SQLModel and runs scans synchronously. These can be
swapped in later without changing the domain/rules layer.
