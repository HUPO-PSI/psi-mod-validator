"""Basic tests for psimod-validator package."""

from psimod_validator import Fix, Issue, PsiModValidator, Severity, ValidationReport


def test_imports():
    """Test that main package imports work."""
    assert PsiModValidator is not None
    assert Issue is not None
    assert Fix is not None
    assert Severity is not None
    assert ValidationReport is not None


def test_severity_enum():
    """Test Severity enum values."""
    assert Severity.ERROR.value == "ERROR"
    assert Severity.WARNING.value == "WARNING"
    assert Severity.INFO.value == "INFO"


def test_issue_creation():
    """Test Issue dataclass."""
    issue = Issue(
        severity=Severity.ERROR,
        mod_id="MOD:00046",
        category="smiles",
        message="Missing SMILES",
    )
    assert issue.severity == Severity.ERROR
    assert issue.mod_id == "MOD:00046"
    assert issue.fix is None


def test_issue_with_fix():
    """Test Issue with a Fix attached."""
    fix = Fix(
        mod_id="MOD:00046",
        xref_key="SMILES",
        old_value="CC",
        new_value="CC",
        reason="Canonicalize",
    )
    issue = Issue(
        severity=Severity.WARNING,
        mod_id="MOD:00046",
        category="smiles",
        message="Not canonical",
        fix=fix,
    )
    assert issue.fix is not None
    assert issue.fix.xref_key == "SMILES"


def test_validation_report():
    """Test ValidationReport properties."""
    error = Issue(Severity.ERROR, "MOD:00001", "smiles", "Invalid SMILES")
    warning = Issue(Severity.WARNING, "MOD:00002", "xref", "Missing xref")
    info = Issue(Severity.INFO, "MOD:00003", "structure", "No description")
    fixable = Issue(
        Severity.WARNING,
        "MOD:00004",
        "smiles",
        "Not canonical",
        fix=Fix("MOD:00004", "SMILES", "CC(O)=O", "CC(=O)O", "Canonicalize"),
    )

    report = ValidationReport(total_terms=100, issues=[error, warning, info, fixable])

    assert report.total_terms == 100
    assert report.error_count == 1
    assert report.warning_count == 2
    assert report.info_count == 1
    assert report.has_errors
    assert len(report.fixable_issues) == 1
