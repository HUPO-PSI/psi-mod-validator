"""Backbone pattern and term_spec validation rules.

Uses RDKit SMARTS substructure matching for backbone connection detection.
"""

from __future__ import annotations

from psimod_validator import _rdkit_utils as rdkit_utils
from psimod_validator._term_data import TermData
from psimod_validator.models import Issue, Severity


class BackbonePatternRule:
    """Validate backbone connection patterns (dummy atoms for N/C terminals).

    Standard amino acid side-chain modifications should have exactly 2 dummy
    atoms: one at the N-terminal (*-N) and one at the C-terminal (C(-*)=O).
    """

    category = "backbone"

    def check(self, term: TermData) -> list[Issue]:
        if term.mol is None:
            return []

        dummy_count = rdkit_utils.count_dummy_atoms(term.mol)
        if dummy_count == 0:
            return []

        issues: list[Issue] = []
        has_n = rdkit_utils.has_n_terminal_dummy(term.mol)
        has_c = rdkit_utils.has_c_terminal_dummy(term.mol)

        if dummy_count == 2 and not (has_n and has_c):
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=(
                        f"Has 2 dummy atoms but unexpected backbone pattern "
                        f"(N-terminal: {has_n}, C-terminal: {has_c})"
                    ),
                )
            )
        elif dummy_count == 1 and not (has_n or has_c):
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message="Has 1 dummy atom but no recognized terminal pattern",
                )
            )
        elif dummy_count > 2:
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=f"Unusual number of dummy atoms: {dummy_count}",
                )
            )

        return issues


class TermSpecConsistencyRule:
    """Check that term_spec annotation is consistent with backbone connectivity.

    Expected patterns:
    - side-chain: 2 dummies, both N-terminal and C-terminal present
    - N-term: 1 dummy, C-terminal present (N is free)
    - C-term: 1 dummy, N-terminal present (C is free)
    """

    category = "backbone"

    def check(self, term: TermData) -> list[Issue]:
        if term.mol is None or term.term_spec is None or term.term_spec == "none":
            return []

        dummy_count = rdkit_utils.count_dummy_atoms(term.mol)
        has_n = rdkit_utils.has_n_terminal_dummy(term.mol)
        has_c = rdkit_utils.has_c_terminal_dummy(term.mol)

        consistent = False
        expected = ""

        if term.term_spec == "side-chain":
            consistent = dummy_count == 2 and has_n and has_c
            expected = "2 dummies with N-terminal and C-terminal connections"
        elif term.term_spec == "N-term":
            consistent = dummy_count == 1 and has_c and not has_n
            expected = "1 dummy at C-terminal (N is free)"
        elif term.term_spec == "C-term":
            consistent = dummy_count == 1 and has_n and not has_c
            expected = "1 dummy at N-terminal (C is free)"
        else:
            return [
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=f"Unknown term_spec value: {term.term_spec!r}",
                )
            ]

        if not consistent:
            return [
                Issue(
                    severity=Severity.ERROR,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=(
                        f"term_spec={term.term_spec!r} inconsistent with SMILES: "
                        f"expected {expected}, found {dummy_count} dummies "
                        f"(N-terminal: {has_n}, C-terminal: {has_c})"
                    ),
                )
            ]
        return []
