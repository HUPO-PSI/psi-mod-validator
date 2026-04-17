"""Report formatting for validation results (file output).

These formatters produce plain strings for writing to files.
The interactive CLI output uses rich directly in __main__.py.
"""

from __future__ import annotations

import json

from psimod_validator.models import ValidationReport


def format_text(report: ValidationReport) -> str:
    """Format a validation report as plain text.

    Parameters
    ----------
    report
        Validation report to format

    Returns
    -------
    str
        Plain text report

    """
    lines = [
        "PSI-MOD Validation Report",
        "=" * 50,
        "",
        f"Terms checked: {report.total_terms}",
        f"Errors:        {report.error_count}",
        f"Warnings:      {report.warning_count}",
        f"Info:          {report.info_count}",
        f"Fixable:       {len(report.fixable_issues)}",
        "",
    ]

    if report.issues:
        lines.append("Issues:")
        lines.append("-" * 50)
        for issue in report.sorted_issues:
            lines.append(
                f"{issue.severity.value:8s}  {issue.mod_id:12s}  "
                f"{issue.category:10s}  {issue.message}"
            )

    return "\n".join(lines)


def format_json(report: ValidationReport) -> str:
    """Format a validation report as JSON.

    Parameters
    ----------
    report
        Validation report to format

    Returns
    -------
    str
        JSON string

    """
    report_dict = {
        "total_terms": report.total_terms,
        "error_count": report.error_count,
        "warning_count": report.warning_count,
        "info_count": report.info_count,
        "fixable_count": len(report.fixable_issues),
        "issues": [
            {
                "severity": issue.severity.value,
                "mod_id": issue.mod_id,
                "category": issue.category,
                "message": issue.message,
                "fixable": issue.fix is not None,
                "fix": (
                    {
                        "xref_key": issue.fix.xref_key,
                        "old_value": issue.fix.old_value,
                        "new_value": issue.fix.new_value,
                        "reason": issue.fix.reason,
                    }
                    if issue.fix
                    else None
                ),
            }
            for issue in report.issues
        ],
    }
    return json.dumps(report_dict, indent=2)


def format_markdown(report: ValidationReport) -> str:
    """Format a validation report as Markdown.

    Parameters
    ----------
    report
        Validation report to format

    Returns
    -------
    str
        Markdown string

    """
    lines = [
        "# PSI-MOD Validation Report",
        "",
        "## Summary",
        "",
        f"- Terms checked: **{report.total_terms}**",
        f"- Errors: **{report.error_count}**",
        f"- Warnings: **{report.warning_count}**",
        f"- Info: **{report.info_count}**",
        f"- Fixable: **{len(report.fixable_issues)}**",
        "",
    ]

    if report.issues:
        lines.extend([
            "## Issues",
            "",
            "| Severity | ID | Category | Message |",
            "|----------|-----|----------|---------|",
        ])
        for issue in report.sorted_issues:
            # Escape pipes in messages for markdown table compatibility
            msg = issue.message.replace("|", "\\|")
            lines.append(
                f"| {issue.severity.value} | {issue.mod_id} | {issue.category} | {msg} |"
            )

    return "\n".join(lines)
