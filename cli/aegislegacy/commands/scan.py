"""Logique de la commande scan : réutilise l'exécuteur partagé avec le backend."""

from __future__ import annotations

from pathlib import Path

from app.domain.findings import Finding
from app.services.scan_runner import ScanTargetNotFoundError, execute_scan
from app.services.scoring import ScoreResult

__all__ = ["ScanTargetNotFoundError", "perform_scan"]


def perform_scan(target: Path, rules_dir: Path) -> tuple[list[Finding], ScoreResult]:
    """Charge les règles depuis `rules_dir` et scanne `target`.

    `target` peut être un fichier unique ou un dossier.
    """
    return execute_scan(target, rules_dir)
