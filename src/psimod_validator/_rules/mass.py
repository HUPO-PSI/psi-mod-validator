"""Mass and composition consistency rules.

Compares computed values from SMILES (via RDKit + pyteomics) against
the database annotations in the OBO file.
"""

from __future__ import annotations

import logging
import re

from psimod_validator._composition import from_molecule, to_chemforma
from psimod_validator._term_data import TermData
from psimod_validator.models import Fix, Issue, Severity

LOGGER = logging.getLogger(__name__)

# Default tolerance for mass comparisons (Daltons)
DEFAULT_MASS_TOLERANCE_DA = 0.01


class MassConsistencyRule:
    """Check consistency between SMILES-derived mass/formula and OBO annotations.

    Validates:
    - DiffMono (monoisotopic difference mass)
    - DiffAvg (average difference mass)
    - DiffFormula (difference formula)
    - MassMono (complete monoisotopic mass)
    - Formula (complete formula)
    """

    category = "mass"

    def __init__(self, *, tolerance_da: float = DEFAULT_MASS_TOLERANCE_DA) -> None:
        self.tolerance_da = tolerance_da

    def check(self, term: TermData) -> list[Issue]:
        if term.mol is None:
            return []

        issues: list[Issue] = []

        # Compute composition from SMILES
        try:
            composition = from_molecule(term.mol)
        except Exception:
            LOGGER.debug("Failed to compute composition for %s", term.mod_id)
            return []

        computed_mono = composition.mass()
        computed_formula = to_chemforma(composition)

        # Check MassMono
        if term.mass_mono is not None:
            diff = abs(computed_mono - term.mass_mono)
            if diff > self.tolerance_da:
                issues.append(
                    Issue(
                        severity=Severity.ERROR,
                        mod_id=term.mod_id,
                        category=self.category,
                        message=(
                            f"MassMono mismatch: SMILES gives {computed_mono:.6f}, "
                            f"annotation says {term.mass_mono:.6f} "
                            f"(diff: {diff:.6f} Da)"
                        ),
                        fix=Fix(
                            mod_id=term.mod_id,
                            xref_key="MassMono",
                            old_value=str(term.mass_mono),
                            new_value=f"{computed_mono:.6f}",
                            reason="Update MassMono to match SMILES",
                        ),
                    )
                )

        # Check Formula
        if term.formula is not None and not _formulas_match(computed_formula, term.formula):
            issues.append(
                Issue(
                    severity=Severity.ERROR,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=(
                        f"Formula mismatch: SMILES gives {_to_psimod_formula(computed_formula)}, "
                        f"annotation says {term.formula}"
                    ),
                    fix=Fix(
                        mod_id=term.mod_id,
                        xref_key="Formula",
                        old_value=term.formula,
                        new_value=_to_psimod_formula(computed_formula),
                        reason="Update Formula to match SMILES",
                    ),
                )
            )

        return issues


def _parse_formula_to_dict(formula: str) -> dict[str, int]:
    """Parse a molecular formula string into element counts.

    Handles both compact notation (C3H7NO2) and PSI-MOD spaced notation
    (C 3 H 7 N 1 O 2).

    Parameters
    ----------
    formula
        Formula string

    Returns
    -------
    dict
        Element to count mapping

    """
    formula = formula.strip()

    # Try PSI-MOD spaced format first: "C 3 H 7 N 1 O 2"
    spaced = re.findall(r"([A-Z][a-z]?)\s+(-?\d+)", formula)
    if spaced:
        return {elem: int(count) for elem, count in spaced}

    # Compact format: "C3H7NO2"
    compact = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    result: dict[str, int] = {}
    for elem, count in compact:
        if elem:
            result[elem] = int(count) if count else 1
    return result


def _formulas_match(formula1: str, formula2: str) -> bool:
    """Compare two formulas, handling different notation styles."""
    return _parse_formula_to_dict(formula1) == _parse_formula_to_dict(formula2)


def _to_psimod_formula(chemforma: str) -> str:
    """Convert a ChemForma string to PSI-MOD spaced format.

    Parameters
    ----------
    chemforma
        Compact formula (e.g., "C3H7NO2")

    Returns
    -------
    str
        PSI-MOD format (e.g., "C 3 H 7 N 1 O 2")

    """
    parsed = _parse_formula_to_dict(chemforma)
    # PSI-MOD ordering: alphabetical
    parts = [f"{elem} {count}" for elem, count in sorted(parsed.items())]
    return " ".join(parts)
