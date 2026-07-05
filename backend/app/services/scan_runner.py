"""Exécution pure d'un scan : charge les règles, lance le moteur, calcule le score.

Partagé par le service backend (qui persiste ensuite le résultat) et par le
CLI (qui l'affiche directement) — évite de réimplémenter deux fois la même
séquence charger-règles / choisir fichier-ou-dossier / scorer.
"""

from __future__ import annotations

from pathlib import Path

from app.domain.findings import Finding
from app.rules.engine import RuleEngine
from app.rules.loader import load_rules_from_directory
from app.services.scoring import ScoreResult, compute_score


class ScanTargetNotFoundError(Exception):
    """Levée quand le chemin à scanner n'existe pas sur le disque."""


def execute_scan(target_path: Path, rules_dir: Path) -> tuple[list[Finding], ScoreResult]:
    if not target_path.exists():
        raise ScanTargetNotFoundError(f"Scan target does not exist: {target_path}")

    rules = load_rules_from_directory(rules_dir)
    engine = RuleEngine(rules)

    if target_path.is_dir():
        findings = engine.scan_tree(target_path)
    else:
        findings = engine.scan_file(target_path, root=target_path.parent)

    return findings, compute_score(findings)
