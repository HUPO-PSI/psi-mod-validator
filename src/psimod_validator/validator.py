"""PSI-MOD ontology validation orchestrator."""

from __future__ import annotations

import logging
from pathlib import Path

from pronto import Ontology
from pronto.term import Term

from psimod_validator._rules import ValidationRule, get_default_rules
from psimod_validator._term_data import extract_term_data
from psimod_validator.models import Issue, Severity, ValidationReport

LOGGER = logging.getLogger(__name__)


class PsiModValidator:
    """Validate PSI-MOD ontology entries.

    Loads an OBO file with pronto, extracts term data, and runs
    validation rules against each non-obsolete term.

    Parameters
    ----------
    ontology_path
        Path to PSI-MOD.obo file
    check_online
        Whether to include rules that verify xrefs via HTTP
    rules
        Custom rule list (uses default rules if not specified)

    """

    def __init__(
        self,
        ontology_path: str | Path,
        *,
        check_online: bool = False,
        rules: list[ValidationRule] | None = None,
    ) -> None:
        self.ontology_path = Path(ontology_path)
        if not self.ontology_path.exists():
            msg = f"Ontology file not found: {ontology_path}"
            raise FileNotFoundError(msg)

        self.ontology = Ontology(str(self.ontology_path))
        self.rules = (
            rules
            if rules is not None
            else get_default_rules(
                check_online=check_online,
            )
        )

    def validate_all(self) -> ValidationReport:
        """Validate all non-obsolete terms in the ontology.

        Returns
        -------
        ValidationReport
            Report with all issues found

        """
        report = ValidationReport(total_terms=0)

        for term in self.ontology.terms():
            if not isinstance(term, Term) or term.obsolete:
                continue

            report.total_terms += 1
            term_data = extract_term_data(term)

            for rule in self.rules:
                report.issues.extend(rule.check(term_data))

        return report

    def validate_term(self, term_id: str) -> list[Issue]:
        """Validate a single term by ID.

        Parameters
        ----------
        term_id
            PSI-MOD accession (e.g., "MOD:00046")

        Returns
        -------
        list[Issue]
            Issues found for this term

        """
        term = self.ontology.get(term_id)
        if term is None:
            return [
                Issue(
                    severity=Severity.ERROR,
                    mod_id=term_id,
                    category="existence",
                    message=f"Term {term_id} not found in ontology",
                )
            ]

        if not isinstance(term, Term):
            return []

        term_data = extract_term_data(term)
        issues = []
        for rule in self.rules:
            issues.extend(rule.check(term_data))
        return issues
