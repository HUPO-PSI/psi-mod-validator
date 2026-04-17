"""Base protocol for validation rules."""

from __future__ import annotations

from typing import Protocol

from psimod_validator._term_data import TermData
from psimod_validator.models import Issue


class ValidationRule(Protocol):
    """Protocol that all validation rules must implement.

    Each rule inspects a single TermData and returns a list of Issues.
    Rules are pure functions of term data — no I/O, no pronto dependency.
    """

    @property
    def category(self) -> str:
        """Issue category string (e.g., 'smiles', 'mass', 'xref')."""
        ...

    def check(self, term: TermData) -> list[Issue]:
        """Run this validation rule against a term.

        Parameters
        ----------
        term
            Extracted term data

        Returns
        -------
        list[Issue]
            Issues found (empty if the term passes)

        """
        ...
