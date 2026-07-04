"""Supported source languages and the file extensions they map to."""

from __future__ import annotations

from enum import StrEnum


class Language(StrEnum):
    PERL = "perl"
    PYTHON = "python"
    SHELL = "shell"
    CONFIG = "config"
    ANY = "any"


LANGUAGE_EXTENSIONS: dict[Language, frozenset[str]] = {
    Language.PERL: frozenset({".pl", ".pm", ".cgi", ".t"}),
    Language.PYTHON: frozenset({".py"}),
    Language.SHELL: frozenset({".sh", ".bash"}),
    Language.CONFIG: frozenset({".conf", ".cfg", ".ini", ".env", ".yaml", ".yml", ".toml"}),
    # ANY has no fixed extensions: rules targeting it are checked against
    # every scanned file (used for cross-language concerns like secrets).
    Language.ANY: frozenset(),
}


def language_for_extension(extension: str) -> Language | None:
    """Return the Language a given file extension belongs to, if any."""
    normalized = extension.lower()
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if normalized in extensions:
            return language
    return None
