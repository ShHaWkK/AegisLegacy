# AegisLegacy CLI

A Typer + Rich CLI built directly on top of the rules engine in
`../backend/app/rules`.

## Install

```bash
# from the repo root
python -m venv .venv
.venv/Scripts/activate      # or: source .venv/bin/activate
pip install -e "backend" -e "cli[dev]"
```

## Commands

- `aegis scan <path>` — scan a file or directory. Prints a findings table
  and a score panel. `--rules-dir` overrides the rule set (defaults to the
  repo's `rules/`, or `$AEGIS_RULES_DIR`). `--output/-o` writes JSON.
  Exits `2` if any critical finding was found, `1` on a scan/rule error.
- `aegis rules list` — list every loaded detection rule.
- `aegis doctor` — check Python version and that the rules directory
  exists and loads without error.

## Not implemented yet

`aegis report generate <scan_id>`, `aegis score <scan_id>` and
`aegis diff <id1> <id2>` are not registered: they operate on a persisted
`scan_id`, which requires the backend API + repository layer (see
`../ROADMAP.md`). Until then, `aegis scan` covers the single-scan use case
directly against a path.

## Tests

```bash
pytest cli/tests
```

Tests insert `../backend` and `cli/` onto `sys.path` via
`cli/tests/conftest.py`, so they run without requiring an editable install
first.
