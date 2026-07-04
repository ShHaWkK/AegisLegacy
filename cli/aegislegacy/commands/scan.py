"""Scan command logic: run the rules engine against a path and score it."""

from __future__ import annotations

from pathlib import Path

from app.domain.findings import Finding
from app.rules.engine import RuleEngine
from app.rules.loader import load_rules_from_directory
from app.services.scoring import ScoreResult, compute_score


def perform_scan(target: Path, rules_dir: Path) -> tuple[list[Finding], ScoreResult]:
    """Load rules from `rules_dir` and scan `target`, returning findings and score.

    `target` may be a single file or a directory; both are supported so the
    CLI can be pointed at a single legacy script as easily as a whole tree.
    """
    if not target.exists():
        raise FileNotFoundError(f"Scan target does not exist: {target}")

    rules = load_rules_from_directory(rules_dir)
    engine = RuleEngine(rules)

    if target.is_dir():
        findings = engine.scan_tree(target)
    else:
        findings = engine.scan_file(target, root=target.parent)

    return findings, compute_score(findings)
