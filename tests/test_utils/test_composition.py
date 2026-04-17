"""Tests for composition utilities."""

import pytest
from pyteomics import mass
from rdkit import Chem

from psimod_validator._composition import from_molecule, get_residue_composition, to_chemforma


def test_from_molecule():
    """Test RDKit molecule to composition conversion."""
    mol = Chem.MolFromSmiles("CC(N)C(=O)O")
    comp = from_molecule(mol)

    assert comp["C"] == 3
    assert comp["H"] == 7
    assert comp["N"] == 1
    assert comp["O"] == 2


def test_from_molecule_with_dummy_atoms():
    """Test that dummy atoms are excluded."""
    mol = Chem.MolFromSmiles("*NC(C)C(*)=O")
    comp = from_molecule(mol)

    assert "*" not in comp
    assert comp["C"] == 3
    assert comp["N"] == 1
    assert comp["O"] == 1


def test_to_chemforma():
    """Test ChemForma formatting."""
    comp = mass.Composition({"C": 3, "H": 7, "N": 1, "O": 2})
    formula = to_chemforma(comp)
    assert formula == "C3H7NO2"


def test_to_chemforma_single_atoms():
    """Test ChemForma formatting with count=1."""
    comp = mass.Composition({"C": 1, "H": 1})
    formula = to_chemforma(comp)
    assert formula == "CH"


def test_get_residue_composition():
    """Test standard amino acid composition lookup."""
    comp = get_residue_composition("A")
    assert comp["C"] == 3
    assert comp["H"] == 5
    assert comp["N"] == 1
    assert comp["O"] == 1


def test_get_residue_composition_invalid():
    """Test invalid residue code."""
    with pytest.raises(KeyError):
        get_residue_composition("X")
