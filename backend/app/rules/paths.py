"""Chemin par défaut du dossier de règles, partagé par le backend et le CLI.

Volontairement sans dépendance à pydantic-settings : le CLI importe cette
fonction directement depuis `app.rules`, sans avoir besoin d'installer
l'extra `api` du backend.
"""

from __future__ import annotations

from pathlib import Path


def default_rules_dir() -> Path:
    """Le dossier rules/ à la racine de ce monorepo."""
    return Path(__file__).resolve().parents[3] / "rules"
