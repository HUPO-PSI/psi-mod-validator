"""SMILES validation rules.

All structural checks use RDKit molecule objects, not string operations.
"""

from __future__ import annotations

from psimod_validator import _rdkit_utils as rdkit_utils
from psimod_validator._term_data import TermData
from psimod_validator.models import Fix, Issue, Severity


class SmilesParseRule:
    """Check that SMILES, when present, can be parsed by RDKit."""

    category = "smiles"

    def check(self, term: TermData) -> list[Issue]:
        if term.smiles is None:
            return []
        if term.mol is None:
            return [
                Issue(
                    severity=Severity.ERROR,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=f"Invalid SMILES (RDKit cannot parse): `{term.smiles}`",
                )
            ]
        return []


class SmilesCanonicalRule:
    """Check that SMILES is in canonical form (with stereochemistry)."""

    category = "smiles"

    def check(self, term: TermData) -> list[Issue]:
        if term.smiles is None or term.mol is None:
            return []
        if rdkit_utils.is_canonical(term.smiles, term.mol):
            return []

        canonical = rdkit_utils.canonicalize(term.mol)
        return [
            Issue(
                severity=Severity.WARNING,
                mod_id=term.mod_id,
                category=self.category,
                message=f"SMILES not in canonical form: `{term.smiles}` -> `{canonical}`",
                fix=Fix(
                    mod_id=term.mod_id,
                    xref_key="SMILES",
                    old_value=term.smiles,
                    new_value=canonical,
                    reason="Canonicalize SMILES",
                ),
            )
        ]


class SmilesValenceRule:
    """Check for valence errors using RDKit sanitization."""

    category = "smiles"

    def check(self, term: TermData) -> list[Issue]:
        if term.mol is None:
            return []
        problems = rdkit_utils.check_valence(term.mol)
        return [
            Issue(
                severity=Severity.ERROR,
                mod_id=term.mod_id,
                category=self.category,
                message=f"Valence error: {problem}",
            )
            for problem in problems
        ]


class SmilesStereochemistryRule:
    """Check for undefined stereocenters in the SMILES structure."""

    category = "smiles"

    def check(self, term: TermData) -> list[Issue]:
        if term.mol is None:
            return []
        undefined = rdkit_utils.find_undefined_stereocenters(term.mol)
        if not undefined:
            return []
        return [
            Issue(
                severity=Severity.WARNING,
                mod_id=term.mod_id,
                category=self.category,
                message=(
                    f"Undefined stereocenter(s) at atom index(es): "
                    f"{', '.join(str(i) for i in undefined)}"
                ),
            )
        ]
