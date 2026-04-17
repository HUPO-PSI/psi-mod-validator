"""Chemical composition and formula utilities.

Bridges RDKit molecule objects and pyteomics Composition for mass
calculations and formula formatting.
"""

from __future__ import annotations

import re
from collections import Counter

from pyteomics import mass
from rdkit import Chem

# Common compositions
H2O_COMPOSITION = mass.Composition({"H": 2, "O": 1})
H2O_MASS: float = H2O_COMPOSITION.mass()
H_COMPOSITION = mass.Composition({"H": 1})
H_MASS: float = H_COMPOSITION.mass()

# Standard amino acid residue compositions (backbone: -H2O from free form)
_RESIDUE_COMPOSITIONS: dict[str, dict[str, int]] = {
    "G": {"C": 2, "H": 3, "N": 1, "O": 1},
    "A": {"C": 3, "H": 5, "N": 1, "O": 1},
    "V": {"C": 5, "H": 9, "N": 1, "O": 1},
    "L": {"C": 6, "H": 11, "N": 1, "O": 1},
    "I": {"C": 6, "H": 11, "N": 1, "O": 1},
    "P": {"C": 5, "H": 7, "N": 1, "O": 1},
    "F": {"C": 9, "H": 9, "N": 1, "O": 1},
    "W": {"C": 11, "H": 10, "N": 2, "O": 1},
    "M": {"C": 5, "H": 9, "N": 1, "O": 1, "S": 1},
    "S": {"C": 3, "H": 5, "N": 1, "O": 2},
    "T": {"C": 4, "H": 7, "N": 1, "O": 2},
    "C": {"C": 3, "H": 5, "N": 1, "O": 1, "S": 1},
    "Y": {"C": 9, "H": 9, "N": 1, "O": 2},
    "H": {"C": 6, "H": 7, "N": 3, "O": 1},
    "D": {"C": 4, "H": 5, "N": 1, "O": 3},
    "E": {"C": 5, "H": 7, "N": 1, "O": 3},
    "N": {"C": 4, "H": 6, "N": 2, "O": 2},
    "Q": {"C": 5, "H": 8, "N": 2, "O": 2},
    "K": {"C": 6, "H": 12, "N": 2, "O": 1},
    "R": {"C": 6, "H": 12, "N": 4, "O": 1},
}


def from_molecule(mol: Chem.Mol) -> mass.Composition:
    """Convert an RDKit molecule to a pyteomics Composition.

    Adds explicit hydrogens and excludes dummy atoms (*).

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    mass.Composition
        Chemical composition

    """
    atom_counts: Counter[str] = Counter(atom.GetSymbol() for atom in Chem.AddHs(mol).GetAtoms())
    atom_counts.pop("*", None)
    return mass.Composition(dict(atom_counts))


def to_chemforma(composition: mass.Composition) -> str:
    """Convert a pyteomics Composition to a ChemForma formula string.

    Elements are ordered: C, H, then alphabetical. Isotope-labelled
    elements use bracket notation (e.g., [13C2]).

    Parameters
    ----------
    composition
        Chemical composition to convert

    Returns
    -------
    str
        ChemForma formatted string (e.g., "C3H7NO2")

    """
    parsed_elements = [(_parse_element(elem), count) for elem, count in composition.items()]

    c = [(elem, isotope, count) for (elem, isotope), count in parsed_elements if elem == "C"]
    h = [(elem, isotope, count) for (elem, isotope), count in parsed_elements if elem == "H"]
    other = [
        (elem, isotope, count)
        for (elem, isotope), count in parsed_elements
        if elem not in {"C", "H"}
    ]
    other.sort(key=lambda x: x[0])

    ordered_elements = c + h + other
    formula_parts = [
        f"[{isotope}{elem}{count if count != 1 else ''}]"
        if isotope
        else f"{elem}{count if count != 1 else ''}"
        for elem, isotope, count in ordered_elements
    ]
    return "".join(formula_parts)


def get_residue_composition(aa: str) -> mass.Composition:
    """Get the residue composition for a standard amino acid.

    Parameters
    ----------
    aa
        Single-letter amino acid code

    Returns
    -------
    mass.Composition
        Residue composition (backbone form, without terminal H2O)

    Raises
    ------
    KeyError
        If the amino acid code is not recognized

    """
    if aa not in _RESIDUE_COMPOSITIONS:
        msg = f"Unknown amino acid code: {aa!r}"
        raise KeyError(msg)
    return mass.Composition(_RESIDUE_COMPOSITIONS[aa])


def _parse_element(element: str) -> tuple[str, int | None]:
    """Parse an element string into element name and optional isotope number.

    Parameters
    ----------
    element
        Element string, optionally with isotope (e.g., "C", "C[13]")

    Returns
    -------
    tuple
        (element_name, isotope_number or None)

    """
    match = re.match(r"([A-Z][a-z]*)(\[\d+\])?", element)
    if match:
        elem, isotope = match.groups()
        isotope_num = int(isotope.strip("[]")) if isotope else None
        return (elem, isotope_num)
    return (element, None)
