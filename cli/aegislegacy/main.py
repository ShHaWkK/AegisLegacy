"""AegisLegacy CLI entry point.

Only commands backed by real, working functionality are registered here.
`report generate`, `score <scan_id>` and `diff` require the scan
persistence layer (backend API + repositories), which does not exist yet
in this iteration — see ROADMAP.md. `scan` already prints a score inline,
so it covers the single-scan use case in the meantime.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from app.domain.severity import Severity
from app.rules.loader import RuleLoadError
from rich.console import Console

from aegislegacy.commands.doctor import run_doctor
from aegislegacy.commands.rules import list_rules
from aegislegacy.commands.scan import perform_scan
from aegislegacy.config.settings import load_settings
from aegislegacy.output.tables import (
    render_doctor_table,
    render_findings_table,
    render_rules_table,
    render_score_panel,
)

app = typer.Typer(
    name="aegis",
    help="AegisLegacy — scan and score legacy Perl/Python codebases.",
    no_args_is_help=True,
)
rules_app = typer.Typer(help="Inspect the loaded detection rules.")
app.add_typer(rules_app, name="rules")

console = Console()

_RULES_DIR_OPTION = typer.Option(
    None, "--rules-dir", help="Override the rules dir (default: repo rules/ or $AEGIS_RULES_DIR)"
)


@app.command()
def scan(
    path: Path = typer.Argument(..., exists=True, help="File or directory to scan."),
    rules_dir: Path | None = _RULES_DIR_OPTION,
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write findings and score as JSON to this file."
    ),
) -> None:
    """Scan PATH for security and modernization findings."""
    settings = load_settings(rules_dir)

    try:
        findings, score = perform_scan(path, settings.rules_dir)
    except (FileNotFoundError, RuleLoadError) as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        raise typer.Exit(code=1) from exc

    if findings:
        console.print(render_findings_table(findings))
    else:
        console.print("[bold green]No findings.[/]")
    console.print(render_score_panel(score))

    if output is not None:
        payload = {
            "target": str(path),
            "score": score.score,
            "classification": score.classification,
            "findings": [finding.as_dict() for finding in findings],
        }
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"Findings written to [bold]{output}[/]")

    if score.findings_by_severity[Severity.CRITICAL] > 0:
        raise typer.Exit(code=2)


@rules_app.command("list")
def rules_list(rules_dir: Path | None = _RULES_DIR_OPTION) -> None:
    """List every detection rule currently loaded."""
    settings = load_settings(rules_dir)

    try:
        rules = list_rules(settings.rules_dir)
    except RuleLoadError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(render_rules_table(rules))


@app.command()
def doctor(rules_dir: Path | None = _RULES_DIR_OPTION) -> None:
    """Check that the local environment is correctly configured."""
    settings = load_settings(rules_dir)
    checks = run_doctor(settings.rules_dir)
    console.print(render_doctor_table(checks))

    if not all(check.passed for check in checks):
        raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
