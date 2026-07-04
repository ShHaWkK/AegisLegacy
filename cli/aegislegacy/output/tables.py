"""Rich renderables for the CLI's terminal output."""

from __future__ import annotations

from app.domain.findings import Finding
from app.domain.severity import Severity, severity_rank
from app.rules.schema import RuleDefinition
from app.services.scoring import ScoreResult
from rich.panel import Panel
from rich.table import Table

from aegislegacy.commands.doctor import DoctorCheck

_SEVERITY_STYLE: dict[Severity, str] = {
    Severity.CRITICAL: "bold white on red",
    Severity.HIGH: "bold red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "cyan",
    Severity.INFO: "dim",
}

_CLASSIFICATION_STYLE: dict[str, str] = {
    "Excellent": "bold green",
    "Good": "green",
    "Needs improvement": "yellow",
    "Risky": "bold yellow",
    "Critical": "bold red",
}


def render_findings_table(findings: list[Finding]) -> Table:
    table = Table(title="Findings", expand=True)
    table.add_column("Severity")
    table.add_column("Rule ID")
    table.add_column("File")
    table.add_column("Line", justify="right")
    table.add_column("Title")

    for finding in sorted(findings, key=lambda f: (severity_rank(f.severity), f.file_path)):
        style = _SEVERITY_STYLE[finding.severity]
        table.add_row(
            f"[{style}]{finding.severity.value.upper()}[/]",
            finding.rule_id,
            finding.file_path,
            str(finding.line_number),
            finding.title,
        )
    return table


def render_score_panel(result: ScoreResult) -> Panel:
    style = _CLASSIFICATION_STYLE.get(result.classification, "white")
    breakdown = ", ".join(
        f"{severity.value}: {count}"
        for severity, count in result.findings_by_severity.items()
        if count
    )
    body = f"[{style}]{result.score:.1f}/100 — {result.classification}[/]"
    if breakdown:
        body += f"\n{breakdown}"
    return Panel(body, title="Security score")


def render_rules_table(rules: list[RuleDefinition]) -> Table:
    table = Table(title="Loaded rules", expand=True)
    table.add_column("ID")
    table.add_column("Language")
    table.add_column("Severity")
    table.add_column("Category")
    table.add_column("Title")

    for rule in sorted(rules, key=lambda r: r.id):
        style = _SEVERITY_STYLE[rule.severity]
        table.add_row(
            rule.id,
            rule.language.value,
            f"[{style}]{rule.severity.value.upper()}[/]",
            rule.category,
            rule.title,
        )
    return table


def render_doctor_table(checks: list[DoctorCheck]) -> Table:
    table = Table(title="Environment checks", expand=True)
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")

    for check in checks:
        status = "[bold green]OK[/]" if check.passed else "[bold red]FAIL[/]"
        table.add_row(check.name, status, check.detail)
    return table
