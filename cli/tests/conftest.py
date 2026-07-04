"""Shared pytest configuration.

Puts both cli/ (for `aegislegacy`) and ../backend (for `app`) on sys.path,
so tests run without requiring editable installs first.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CLI_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = CLI_ROOT.parent / "backend"

for path in (CLI_ROOT, BACKEND_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

_EVAL_RULE = """
id: PY-EVAL-001
language: python
severity: high
title: Use of eval()
patterns:
  - "\\\\beval\\\\s*\\\\("
description: Detects eval() usage.
recommendation: Avoid eval().
category: unsafe-eval
"""


@pytest.fixture
def rules_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "rules"
    directory.mkdir()
    (directory / "eval.yaml").write_text(_EVAL_RULE, encoding="utf-8")
    return directory


@pytest.fixture
def legacy_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / "script.py").write_text("result = eval(user_input)\n", encoding="utf-8")
    (project / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return project
