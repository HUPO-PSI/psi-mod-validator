"""Tests for RDKit utilities."""

from psimod_validator import _rdkit_utils as rdkit_utils


class TestParseSmiles:
    def test_valid_smiles(self):
        mol = rdkit_utils.parse_smiles("CC(=O)O")
        assert mol is not None

    def test_invalid_smiles(self):
        assert rdkit_utils.parse_smiles("invalid") is None

    def test_empty_smiles(self):
        assert rdkit_utils.parse_smiles("") is None
        assert rdkit_utils.parse_smiles("  ") is None


class TestCanonicalize:
    def test_canonical(self):
        mol = rdkit_utils.parse_smiles("CC(=O)O")
        canonical = rdkit_utils.canonicalize(mol)
        assert canonical == "CC(=O)O"

    def test_preserves_stereochemistry(self):
        mol = rdkit_utils.parse_smiles("C[C@H](N)C(=O)O")
        canonical = rdkit_utils.canonicalize(mol)
        assert "@" in canonical

    def test_is_canonical_true(self):
        smiles = "CC(=O)O"
        mol = rdkit_utils.parse_smiles(smiles)
        assert rdkit_utils.is_canonical(smiles, mol)


class TestDummyAtoms:
    def test_count_dummy_atoms_two(self):
        # Standard amino acid backbone: *NC(...)C(*)=O
        mol = rdkit_utils.parse_smiles("*NC(C)C(*)=O")
        assert rdkit_utils.count_dummy_atoms(mol) == 2

    def test_count_dummy_atoms_zero(self):
        mol = rdkit_utils.parse_smiles("CC(=O)O")
        assert rdkit_utils.count_dummy_atoms(mol) == 0

    def test_n_terminal_dummy(self):
        mol = rdkit_utils.parse_smiles("*NC(C)C(*)=O")
        assert rdkit_utils.has_n_terminal_dummy(mol)

    def test_c_terminal_dummy(self):
        mol = rdkit_utils.parse_smiles("*NC(C)C(*)=O")
        assert rdkit_utils.has_c_terminal_dummy(mol)

    def test_no_n_terminal_without_dummy(self):
        mol = rdkit_utils.parse_smiles("CC(=O)O")
        assert not rdkit_utils.has_n_terminal_dummy(mol)

    def test_canonical_smiles_still_detected(self):
        """Backbone detection must work on canonical SMILES, not just input form."""
        mol = rdkit_utils.parse_smiles("C[C@H](N-*)C(-*)=O")
        # RDKit may rewrite this; the SMARTS must still detect patterns
        assert rdkit_utils.has_n_terminal_dummy(mol)
        assert rdkit_utils.has_c_terminal_dummy(mol)
        assert rdkit_utils.count_dummy_atoms(mol) == 2


class TestChemicalProperties:
    def test_formal_charge_neutral(self):
        mol = rdkit_utils.parse_smiles("CC(=O)O")
        assert rdkit_utils.get_formal_charge(mol) == 0

    def test_formal_charge_positive(self):
        mol = rdkit_utils.parse_smiles("[NH3+]CC(=O)O")
        assert rdkit_utils.get_formal_charge(mol) == 1

    def test_molecular_formula(self):
        mol = rdkit_utils.parse_smiles("CC(=O)O")
        formula = rdkit_utils.get_molecular_formula(mol)
        assert formula == "C2H4O2"

    def test_undefined_stereocenters(self):
        # Alanine without stereo specification
        mol = rdkit_utils.parse_smiles("CC(N)C(=O)O")
        undefined = rdkit_utils.find_undefined_stereocenters(mol)
        assert len(undefined) > 0

    def test_defined_stereocenters(self):
        mol = rdkit_utils.parse_smiles("C[C@H](N)C(=O)O")
        undefined = rdkit_utils.find_undefined_stereocenters(mol)
        assert len(undefined) == 0
