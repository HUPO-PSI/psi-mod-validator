"""Command-line interface for PSI-MOD validation and curation."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from psimod_validator._output import format_json, format_markdown, format_text
from psimod_validator.fixer import apply_fixes, write_obo
from psimod_validator.models import Issue, Severity, ValidationReport
from psimod_validator.validator import PsiModValidator

console = Console()

_SEVERITY_STYLE = {
    Severity.ERROR: "bold red",
    Severity.WARNING: "yellow",
    Severity.INFO: "dim",
}


def _print_summary(report: ValidationReport) -> None:
    """Print a summary panel of validation results."""
    console.print()
    console.print(f"  Terms checked: [bold]{report.total_terms}[/]")
    console.print(f"  Errors:        [bold red]{report.error_count}[/]")
    console.print(f"  Warnings:      [bold yellow]{report.warning_count}[/]")
    console.print(f"  Info:          [dim]{report.info_count}[/]")
    console.print(f"  Fixable:       [bold cyan]{len(report.fixable_issues)}[/]")


def _print_issues(issues: list[Issue]) -> None:
    """Print issues as a rich table."""
    if not issues:
        return

    table = Table(show_header=True, header_style="bold", pad_edge=False, box=None)
    table.add_column("Severity", width=9)
    table.add_column("ID", width=12)
    table.add_column("Category", width=10)
    table.add_column("Message")

    for issue in issues:
        style = _SEVERITY_STYLE.get(issue.severity, "")
        table.add_row(
            Text(issue.severity.value, style=style),
            issue.mod_id,
            issue.category,
            issue.message,
        )

    console.print()
    console.print(table)


@click.group()
@click.version_option()
def cli() -> None:
    """PSI-MOD validation and curation tools."""


@cli.command()
@click.argument("ontology", type=click.Path(exists=True, path_type=Path))
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.option("--check-online", is_flag=True, help="Verify xrefs exist online (slow)")
@click.option("--fix", is_flag=True, help="Apply auto-fixable changes")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write report to file")
@click.option(
    "--format",
    "format_type",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Report format",
)
def validate(
    ontology: Path,
    strict: bool,
    check_online: bool,
    fix: bool,
    output: Path | None,
    format_type: str,
) -> None:
    """Validate PSI-MOD ontology and optionally apply fixes."""
    console.print(f"Validating [bold]{ontology}[/]...")

    validator = PsiModValidator(ontology, check_online=check_online)
    report = validator.validate_all()

    _print_summary(report)

    if output:
        formatters = {"text": format_text, "json": format_json, "markdown": format_markdown}
        content = formatters[format_type](report)
        output.write_text(content)
        console.print(f"\nReport written to [bold]{output}[/]")
    elif report.issues:
        _print_issues(report.sorted_issues)

    # Apply fixes if requested
    if fix and report.fixable_issues:
        fix_report = apply_fixes(validator.ontology, report.issues)
        console.print(f"\n  Fixes applied: [bold green]{fix_report.applied_count}[/]")
        if fix_report.skipped_count > 0:
            console.print(f"  Fixes skipped: [bold yellow]{fix_report.skipped_count}[/]")

        fixed_path = ontology.with_stem(ontology.stem + ".fixed")
        write_obo(validator.ontology, fixed_path)
        console.print(f"  Fixed ontology written to [bold]{fixed_path}[/]")

    # Exit code
    if report.has_errors or (strict and report.warning_count > 0):
        raise SystemExit(1)


@cli.command()
@click.argument("mod_ids", nargs=-1, required=True)
@click.option(
    "--ontology",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to PSI-MOD.obo",
)
def check(mod_ids: tuple[str, ...], ontology: Path) -> None:
    """Check specific modifications by MOD ID."""
    validator = PsiModValidator(ontology)

    for mod_id in mod_ids:
        console.print(f"\nChecking [bold]{mod_id}[/]...")
        issues = validator.validate_term(mod_id)

        if not issues:
            console.print("  [green]No issues found[/]")
        else:
            for issue in issues:
                style = _SEVERITY_STYLE.get(issue.severity, "")
                console.print(
                    f"  [{style}]{issue.severity.value}[/]: "
                    f"[dim]\\[{issue.category}][/] {issue.message}"
                )


if __name__ == "__main__":
    cli()
