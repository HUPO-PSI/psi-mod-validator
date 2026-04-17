"""Apply fixes to a PSI-MOD OBO ontology.

Modifies pronto Term xrefs based on Fix objects from validation issues,
then writes the corrected OBO file.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from pronto import Ontology
from pronto.term import Term
from pronto.xref import Xref

from psimod_validator.models import Fix, Issue

LOGGER = logging.getLogger(__name__)


@dataclass
class FixReport:
    """Summary of fixes applied.

    Attributes
    ----------
    applied
        Fixes that were successfully applied
    skipped
        Fixes that could not be applied (with reason)

    """

    applied: list[Fix] = field(default_factory=list)
    skipped: list[tuple[Fix, str]] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        """Number of fixes applied."""
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        """Number of fixes skipped."""
        return len(self.skipped)


def apply_fixes(ontology: Ontology, issues: list[Issue]) -> FixReport:
    """Apply all fixable issues to an ontology in-place.

    Parameters
    ----------
    ontology
        Pronto Ontology object (modified in-place)
    issues
        Validation issues (only those with fix != None are applied)

    Returns
    -------
    FixReport
        Summary of applied and skipped fixes

    """
    report = FixReport()

    fixes = [issue.fix for issue in issues if issue.fix is not None]

    for fix in fixes:
        term = ontology.get(fix.mod_id)
        if term is None or not isinstance(term, Term):
            report.skipped.append((fix, f"Term {fix.mod_id} not found"))
            continue

        try:
            _apply_xref_fix(term, fix)
            report.applied.append(fix)
        except Exception as e:
            LOGGER.debug("Failed to apply fix for %s: %s", fix.mod_id, e)
            report.skipped.append((fix, str(e)))

    return report


def write_obo(ontology: Ontology, output_path: Path) -> None:
    """Write an ontology to an OBO file.

    Parameters
    ----------
    ontology
        Pronto Ontology object
    output_path
        Path to write the OBO file

    """
    with output_path.open("wb") as f:
        ontology.dump(f, format="obo")


def _apply_xref_fix(term: Term, fix: Fix) -> None:
    """Apply a single xref fix to a term.

    In pronto, PSI-MOD annotations are stored as Xref objects where
    id='KEY:' (with trailing colon) and description='VALUE'.
    term.xrefs is a frozenset, so we must replace it entirely.

    Parameters
    ----------
    term
        Pronto Term to modify
    fix
        Fix to apply

    """
    xref_key = f"{fix.xref_key}:"  # Add trailing colon for pronto format

    # Build new xref set: replace matching xref or add new one
    new_xrefs: set[Xref] = set()
    found = False

    for xref in term.xrefs:
        if xref.id == xref_key:
            new_xrefs.add(Xref(id=xref_key, description=fix.new_value))
            found = True
        else:
            new_xrefs.add(xref)

    if not found:
        # Add new xref if it didn't exist
        new_xrefs.add(Xref(id=xref_key, description=fix.new_value))

    term.xrefs = frozenset(new_xrefs)
