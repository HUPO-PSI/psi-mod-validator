"""Formal charge validation rule.

Compares RDKit-computed formal charge against the FormalCharge xref annotation.
"""

from __future__ import annotations

from psimod_validator import _rdkit_utils as rdkit_utils
from psimod_validator._term_data import TermData
from psimod_validator.models import Fix, Issue, Severity


def _format_charge(charge: int) -> str:
    """Format an integer charge into PSI-MOD notation (e.g., '1+', '2-')."""
    if charge == 0:
        return "0"
    sign = "+" if charge > 0 else "-"
    return f"{abs(charge)}{sign}"


class FormalChargeRule:
    """Check FormalCharge annotation matches RDKit-computed charge."""

    category = "charge"

    def check(self, term: TermData) -> list[Issue]:
        if term.mol is None:
            return []

        computed_charge = rdkit_utils.get_formal_charge(term.mol)

        if term.formal_charge is not None:
            if computed_charge != term.formal_charge:
                return [
                    Issue(
                        severity=Severity.ERROR,
                        mod_id=term.mod_id,
                        category=self.category,
                        message=(
                            f"FormalCharge mismatch: SMILES gives {computed_charge}, "
                            f"annotation says {term.formal_charge}"
                        ),
                        fix=Fix(
                            mod_id=term.mod_id,
                            xref_key="FormalCharge",
                            old_value=_format_charge(term.formal_charge),
                            new_value=_format_charge(computed_charge),
                            reason="Update FormalCharge to match SMILES",
                        ),
                    )
                ]
        elif computed_charge != 0:
            # Molecule has a charge but no FormalCharge annotation
            return [
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=(
                        f"SMILES has formal charge {computed_charge} but no FormalCharge annotation"
                    ),
                    fix=Fix(
                        mod_id=term.mod_id,
                        xref_key="FormalCharge",
                        old_value=None,
                        new_value=_format_charge(computed_charge),
                        reason="Add missing FormalCharge annotation",
                    ),
                )
            ]
        return []
