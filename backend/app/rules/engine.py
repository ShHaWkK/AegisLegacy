"""Applies loaded rules against files and directory trees.

The engine is intentionally I/O-light and side-effect free: given rules and
a path, it returns normalized `Finding` objects. Orchestration (which paths
to scan, what to do with findings) belongs to the scanners/services layer.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from re import Pattern

from app.domain.findings import Finding
from app.domain.language import Language, language_for_extension
from app.rules.schema import RuleDefinition

IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        "venv",
        ".venv",
        "blib",
        "_build",
        ".idea",
        ".vscode",
    }
)


class _CompiledRule:
    """A rule paired with its precompiled regex patterns."""

    __slots__ = ("definition", "patterns")

    def __init__(self, definition: RuleDefinition) -> None:
        self.definition = definition
        self.patterns: list[Pattern[str]] = definition.compiled_patterns()


class RuleEngine:
    """Matches a fixed set of rules against source files."""

    def __init__(self, rules: list[RuleDefinition]) -> None:
        self._compiled_rules = [_CompiledRule(rule) for rule in rules]
        self._has_any_language_rule = any(
            rule.language is Language.ANY for rule in rules
        )

    @property
    def rules(self) -> list[RuleDefinition]:
        return [compiled.definition for compiled in self._compiled_rules]

    def scan_file(self, path: Path, root: Path) -> list[Finding]:
        """Scan a single file and return the findings it produced.

        `root` is used to compute the finding's relative file path so
        reports do not leak absolute filesystem layout.
        """
        content = self._read_text(path)
        if content is None:
            return []

        file_language = language_for_extension(path.suffix)
        relevant_rules = [
            compiled
            for compiled in self._compiled_rules
            if compiled.definition.language is Language.ANY
            or compiled.definition.language is file_language
        ]
        if not relevant_rules:
            return []

        relative_path = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)

        findings: list[Finding] = []
        for compiled in relevant_rules:
            findings.extend(
                self._match_rule(compiled, content=content, relative_path=relative_path)
            )
        return findings

    def scan_tree(self, root: Path) -> list[Finding]:
        """Recursively scan every relevant file under `root`."""
        findings: list[Finding] = []
        for path in self._iter_candidate_files(root):
            findings.extend(self.scan_file(path, root))
        return findings

    def _iter_candidate_files(self, root: Path) -> Iterator[Path]:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORED_DIRECTORIES for part in path.relative_to(root).parts):
                continue
            if self._has_any_language_rule or language_for_extension(path.suffix) is not None:
                yield path

    @staticmethod
    def _read_text(path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            # Binary or unreadable files are skipped rather than failing
            # the whole scan; legacy trees routinely contain such files.
            return None

    @staticmethod
    def _match_rule(
        compiled: _CompiledRule, *, content: str, relative_path: str
    ) -> list[Finding]:
        definition = compiled.definition
        findings: list[Finding] = []
        for pattern in compiled.patterns:
            for match in pattern.finditer(content):
                line_number = content.count("\n", 0, match.start()) + 1
                findings.append(
                    Finding(
                        rule_id=definition.id,
                        title=definition.title,
                        severity=definition.severity,
                        category=definition.category,
                        language=definition.language.value,
                        file_path=relative_path,
                        line_number=line_number,
                        matched_text=match.group(0).strip(),
                        description=definition.description,
                        recommendation=definition.recommendation,
                    )
                )
        return findings
