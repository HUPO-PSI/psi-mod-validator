"""Core data models for PSI-MOD validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """Issue severity levels, ordered by decreasing priority."""

    ERROR = (0, "ERROR")
    WARNING = (1, "WARNING")
    INFO = (2, "INFO")

    def __init__(self, order: int, label: str) -> None:
        self.order = order
        self.label = label

    @property
    def value(self) -> str:  # type: ignore[override]
        """Return the human-readable label."""
        return self.label


@dataclass(frozen=True)
class Fix:
    """A concrete fix to apply to an OBO term.

    Attributes
    ----------
    mod_id
        PSI-MOD accession (e.g., "MOD:00046")
    xref_key
        The xref annotation key to modify (e.g., "SMILES", "DiffMono")
    old_value
        Current value (None if the annotation is missing)
    new_value
        Corrected value to write
    reason
        Human-readable explanation of the fix

    """

    mod_id: str
    xref_key: str
    old_value: str | None
    new_value: str
    reason: str


@dataclass
class Issue:
    """A validation issue for a PSI-MOD term.

    Attributes
    ----------
    severity
        Issue severity level
    mod_id
        PSI-MOD accession (e.g., "MOD:00046")
    category
        Issue category (smiles, xref, mass, structure, etc.)
    message
        Human-readable description
    fix
        Optional fix that can be applied to resolve this issue

    """

    severity: Severity
    mod_id: str
    category: str
    message: str
    fix: Fix | None = None

    @property
    def sort_key(self) -> tuple[int, str]:
        """Sort key: severity (errors first), then MOD ID."""
        return (self.severity.order, self.mod_id)


@dataclass
class ValidationReport:
    """Validation results for a PSI-MOD ontology.

    Attributes
    ----------
    total_terms
        Total non-obsolete terms validated
    issues
        All issues found across all terms

    """

    total_terms: int
    issues: list[Issue] = field(default_factory=list)

    @property
    def sorted_issues(self) -> list[Issue]:
        """All issues sorted by severity (errors first), then MOD ID."""
        return sorted(self.issues, key=lambda i: i.sort_key)

    @property
    def errors(self) -> list[Issue]:
        """All ERROR severity issues."""
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        """All WARNING severity issues."""
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def infos(self) -> list[Issue]:
        """All INFO severity issues."""
        return [i for i in self.issues if i.severity == Severity.INFO]

    @property
    def error_count(self) -> int:
        """Number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Number of warnings."""
        return len(self.warnings)

    @property
    def info_count(self) -> int:
        """Number of info items."""
        return len(self.infos)

    @property
    def has_errors(self) -> bool:
        """Whether any errors were found."""
        return self.error_count > 0

    @property
    def fixable_issues(self) -> list[Issue]:
        """Issues that have an auto-fix available."""
        return [i for i in self.issues if i.fix is not None]
