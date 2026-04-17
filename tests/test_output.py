"""Tests for report formatting functions."""

import json

from psimod_validator._output import format_json, format_markdown, format_text
from psimod_validator.models import Fix, Issue, Severity, ValidationReport


def _make_report(**kwargs) -> ValidationReport:
    defaults = {"total_terms": 10}
    defaults.update(kwargs)
    return ValidationReport(**defaults)


def _error(mod_id="MOD:00001", message="Invalid SMILES") -> Issue:
    return Issue(severity=Severity.ERROR, mod_id=mod_id, category="smiles", message=message)


def _warning(mod_id="MOD:00002", message="Not canonical") -> Issue:
    return Issue(severity=Severity.WARNING, mod_id=mod_id, category="smiles", message=message)


def _fixable() -> Issue:
    return Issue(
        severity=Severity.WARNING,
        mod_id="MOD:00003",
        category="smiles",
        message="Non-canonical SMILES",
        fix=Fix(
            mod_id="MOD:00003",
            xref_key="SMILES",
            old_value="OC(C)=O",
            new_value="CC(=O)O",
            reason="Canonicalize",
        ),
    )


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------

class TestFormatText:
    def test_header_present(self):
        report = _make_report()
        text = format_text(report)
        assert "PSI-MOD Validation Report" in text

    def test_counts_in_output(self):
        report = _make_report(total_terms=42, issues=[_error(), _warning()])
        text = format_text(report)
        assert "42" in text
        assert "Errors" in text
        assert "Warnings" in text

    def test_empty_report_no_issues_section(self):
        report = _make_report(issues=[])
        text = format_text(report)
        assert "Issues:" not in text

    def test_issue_line_appears(self):
        report = _make_report(issues=[_error(message="Something broke")])
        text = format_text(report)
        assert "Something broke" in text
        assert "MOD:00001" in text

    def test_severity_order(self):
        # Errors should appear before warnings in sorted output
        report = _make_report(issues=[_warning(), _error()])
        text = format_text(report)
        error_pos = text.index("ERROR")
        warning_pos = text.index("WARNING")
        assert error_pos < warning_pos


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

class TestFormatJson:
    def test_valid_json(self):
        report = _make_report(issues=[_error()])
        result = format_json(report)
        data = json.loads(result)  # must not raise
        assert isinstance(data, dict)

    def test_top_level_keys(self):
        report = _make_report(issues=[_error(), _warning()])
        data = json.loads(format_json(report))
        assert "total_terms" in data
        assert "error_count" in data
        assert "warning_count" in data
        assert "issues" in data

    def test_issue_fields(self):
        report = _make_report(issues=[_error()])
        data = json.loads(format_json(report))
        issue = data["issues"][0]
        assert issue["severity"] == "ERROR"
        assert issue["mod_id"] == "MOD:00001"
        assert issue["fixable"] is False

    def test_fixable_issue_includes_fix(self):
        report = _make_report(issues=[_fixable()])
        data = json.loads(format_json(report))
        issue = data["issues"][0]
        assert issue["fixable"] is True
        assert issue["fix"]["xref_key"] == "SMILES"
        assert issue["fix"]["new_value"] == "CC(=O)O"

    def test_counts_correct(self):
        report = _make_report(issues=[_error(), _warning(), _warning()])
        data = json.loads(format_json(report))
        assert data["error_count"] == 1
        assert data["warning_count"] == 2


# ---------------------------------------------------------------------------
# format_markdown
# ---------------------------------------------------------------------------

class TestFormatMarkdown:
    def test_has_header(self):
        report = _make_report()
        md = format_markdown(report)
        assert "# PSI-MOD Validation Report" in md

    def test_summary_section(self):
        report = _make_report(total_terms=5, issues=[_error()])
        md = format_markdown(report)
        assert "## Summary" in md
        assert "**5**" in md

    def test_issues_table_present(self):
        report = _make_report(issues=[_error()])
        md = format_markdown(report)
        assert "## Issues" in md
        assert "| Severity |" in md

    def test_pipe_in_message_escaped(self):
        issue = Issue(
            severity=Severity.WARNING,
            mod_id="MOD:00001",
            category="smiles",
            message="before | after",
        )
        report = _make_report(issues=[issue])
        md = format_markdown(report)
        assert r"before \| after" in md

    def test_empty_report_no_issues_table(self):
        report = _make_report(issues=[])
        md = format_markdown(report)
        assert "## Issues" not in md
