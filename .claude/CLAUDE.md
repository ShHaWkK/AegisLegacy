# AegisLegacy — permanent instructions for Claude

AegisLegacy is a Python/Perl runtime security & modernization platform for
legacy codebases. It is a portfolio project held to a real senior-engineer
bar — code quality is the product, not a means to a demo.

## Non-negotiables

- Never write draft or placeholder code inside an implemented module. If a
  module isn't ready to be built properly, leave it out of scope and say so
  in `ROADMAP.md` rather than stubbing it with fake logic.
- Respect the architecture: domain (`backend/app/domain`) has no I/O and no
  framework imports; rules/scanners/services orchestrate domain logic;
  api/repositories/workers are the only layers allowed to touch the
  network, filesystem-as-a-side-effect, or a database.
- Every behavior change ships with tests in the same commit. No exceptions
  for "obvious" code — the rules engine's regex behavior is exactly the
  kind of thing that looks obvious and isn't.
- Run `make lint`, `make typecheck`, and `make security` (or the
  equivalent `ruff check`, `mypy app`, `bandit -r app`) before considering
  backend work done. `ruff` and `mypy --strict` must be clean.
- Never introduce a secret, real or fake-but-realistic, outside
  `demo-legacy-app/`. Fake secrets in the demo app must be obviously fake
  (e.g. `hunter2super`, not something that looks like a real key format
  unless it's the point of the fixture).
- Never disable a security rule (bandit, a YAML detection rule, a lint
  rule) without a one-line comment explaining why it's a false positive in
  this exact context.
- Keep functions small and single-purpose. If a function needs a "and
  also" in its docstring, split it.
- Document decisions that aren't obvious from the code (why a regex is
  shaped the way it is, why a severity was chosen) — not what the code
  does.

## Conventions

- Python: 3.12+, full type hints, pydantic v2 for all data crossing a
  boundary (YAML, JSON, HTTP). See `.claude/rules/python-style.md`.
- Perl: `use strict; use warnings;` always, logic lives in `.pm` modules
  under `Aegis::`, not inline in scripts. See `.claude/rules/perl-style.md`.
- Rule IDs follow `<NAMESPACE>-<TOPIC>-<NNN>` (e.g. `PERL-CMD-001`) and
  must stay globally unique across `rules/`.
- Use the Makefile targets instead of ad hoc commands so CI and local dev
  stay identical.

## Where things stand

Check `ROADMAP.md` before assuming a module exists. Only the rules engine
(`backend/app/rules`, `backend/app/domain`, `backend/app/services/scoring.py`)
and its 8 demo rules under `rules/` are implemented and tested as of this
writing.
