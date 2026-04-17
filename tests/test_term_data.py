"""Tests for extract_term_data() and private parsing helpers."""

import pytest

from psimod_validator._term_data import _parse_charge, _parse_float, extract_term_data


class TestExtractTermData:
    def test_full_annotations(self, ontology):
        td = extract_term_data(ontology["MOD:00001"])

        assert td.mod_id == "MOD:00001"
        assert td.name == "L-alanine residue"
        assert td.definition is not None
        assert not td.is_obsolete

        # SMILES and mol
        assert td.smiles == "*N[C@@H](C)C(*)=O"
        assert td.mol is not None

        # Numeric annotations
        assert td.formula == "C 3 H 5 N 1 O 1"
        assert td.mass_mono == pytest.approx(71.037114)
        assert td.mass_avg == pytest.approx(71.079)
        assert td.diff_mono == pytest.approx(-0.984016)
        assert td.diff_avg == pytest.approx(-0.921)

        # String annotations
        assert td.origin == "A"
        assert td.source == "natural"
        assert td.term_spec == "none"

        # External xrefs
        assert td.unimod_id == "7"
        assert td.uniprot_ptm == "PTM-0118"

        # Hierarchy
        assert "MOD:00000" in td.superclass_ids

    def test_def_xrefs_extracted(self, ontology):
        td = extract_term_data(ontology["MOD:00001"])
        assert "PubMed:12345" in td.def_xrefs

    def test_formal_charge_parsed(self, ontology):
        td = extract_term_data(ontology["MOD:00002"])
        assert td.formal_charge == 1

    def test_invalid_smiles_mol_is_none(self, ontology):
        td = extract_term_data(ontology["MOD:00003"])
        assert td.smiles == "invalid_smiles_xyz"
        assert td.mol is None

    def test_root_term_no_parents(self, ontology):
        td = extract_term_data(ontology["MOD:00000"])
        assert td.smiles is None
        assert td.mol is None
        assert td.superclass_ids == []

    def test_obsolete_flag(self, ontology):
        td = extract_term_data(ontology["MOD:00004"])
        assert td.is_obsolete


class TestParseCharge:
    def test_positive_with_digit(self):
        assert _parse_charge("1+") == 1

    def test_negative_with_digit(self):
        assert _parse_charge("2-") == -2

    def test_bare_plus(self):
        assert _parse_charge("+") == 1

    def test_bare_minus(self):
        assert _parse_charge("-") == -1

    def test_zero(self):
        assert _parse_charge("0") == 0

    def test_none_returns_none(self):
        assert _parse_charge(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_charge("") is None

    def test_garbage_returns_none(self):
        assert _parse_charge("garbage") is None

    def test_whitespace_stripped(self):
        assert _parse_charge(" 1+ ") == 1


class TestParseFloat:
    def test_valid_float(self):
        assert _parse_float("71.037114") == pytest.approx(71.037114)

    def test_negative_float(self):
        assert _parse_float("-0.984016") == pytest.approx(-0.984016)

    def test_none_returns_none(self):
        assert _parse_float(None) is None

    def test_non_numeric_returns_none(self):
        assert _parse_float("not-a-number") is None
