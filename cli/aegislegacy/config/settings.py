"""Résout la config du CLI : flag explicite, puis variable d'env, puis défaut.

Ordre de priorité (le premier trouvé gagne) : --rules-dir, la variable
d'environnement AEGIS_RULES_DIR, puis le dossier rules/ du monorepo
(fonctionne directement pour qui lance le CLI depuis ce repo).
"""

from __future__ import annotations

import os
from pathlib import Path

from app.rules.paths import default_rules_dir
from pydantic import BaseModel


class Settings(BaseModel):
    rules_dir: Path


def load_settings(rules_dir: Path | None = None) -> Settings:
    if rules_dir is not None:
        resolved = rules_dir
    elif env_value := os.environ.get("AEGIS_RULES_DIR"):
        resolved = Path(env_value)
    else:
        resolved = default_rules_dir()
    return Settings(rules_dir=resolved)
