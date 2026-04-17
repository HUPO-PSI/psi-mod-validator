"""Ontology structure validation rules.

Validates term names, definitions, and hierarchical relationships.
"""

from __future__ import annotations

from psimod_validator._term_data import TermData
from psimod_validator.models import Issue, Severity

# Known relationship types in PSI-MOD
_KNOWN_RELATIONSHIP_TYPES = frozenset(
    {
        "derives_from",
        "contains",
        "has_functional_parent",
        "part_of",
    }
)


class TermNameRule:
    """Check that every term has a non-empty name."""

    category = "structure"

    def check(self, term: TermData) -> list[Issue]:
        if not term.name:
            return [
                Issue(
                    severity=Severity.ERROR,
                    mod_id=term.mod_id,
                    category=self.category,
                    message="Missing term name",
                )
            ]
        return []


class TermDefinitionRule:
    """Check that every term has a definition."""

    category = "structure"

    def check(self, term: TermData) -> list[Issue]:
        if not term.definition:
            return [
                Issue(
                    severity=Severity.INFO,
                    mod_id=term.mod_id,
                    category=self.category,
                    message="Missing definition",
                )
            ]
        return []


class TermHierarchyRule:
    """Check that terms have at least one parent and use known relationship types."""

    category = "structure"

    def check(self, term: TermData) -> list[Issue]:
        issues: list[Issue] = []

        # Root term MOD:00000 is allowed to have no parents
        if term.mod_id == "MOD:00000":
            return []

        if not term.superclass_ids and not term.relationships:
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message="Term has no parent (no is_a or relationship)",
                )
            )

        # Check for unknown relationship types
        for rel_type in term.relationships:
            if rel_type not in _KNOWN_RELATIONSHIP_TYPES:
                issues.append(
                    Issue(
                        severity=Severity.WARNING,
                        mod_id=term.mod_id,
                        category=self.category,
                        message=f"Unknown relationship type: {rel_type!r}",
                    )
                )

        return issues
