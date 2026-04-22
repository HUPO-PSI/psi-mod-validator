"""Tests for MassConsistencyRule and formula helper functions."""

from psimod_validator._composition import from_molecule, to_chemforma
from psimod_validator._rdkit_utils import parse_smiles
from psimod_validator._rules.mass import (
    MassConsistencyRule,
    _formulas_match,
    _parse_formula_to_dict,
    _to_psimod_formula,
)
from psimod_validator._term_data import TermData
from psimod_validator.models import Severity


def _make_term(**kwargs) -> TermData:
    defaults = {"mod_id": "MOD:99999", "name": "test", "is_obsolete": False}
    defaults.update(kwargs)
    if "smiles" in defaults and defaults.get("mol") is None:
        defaults["mol"] = parse_smiles(defaults["smiles"])
    return TermData(**defaults)


# ---------------------------------------------------------------------------
# MassConsistencyRule
# ---------------------------------------------------------------------------


class TestMassConsistencyRule:
    rule = MassConsistencyRule()

    # Compute reference values from the library itself so tests don't hardcode masses.
    _mol = parse_smiles("CC(=O)O")
    _comp = from_molecule(_mol)
    _exact_mass = _comp.mass()
    _chemforma = to_chemforma(_comp)  # compact: "C2H4O2"
    _psimod_formula = _to_psimod_formula(_chemforma)  # spaced: "C 2 H 4 O 2"

    def test_no_mol_no_issues(self):
        term = _make_term()
        assert self.rule.check(term) == []

    def test_no_annotations_no_issues(self):
        # mol present but no mass/formula annotation to validate against
        term = _make_term(smiles="CC(=O)O")
        assert self.rule.check(term) == []

    def test_matching_mass_mono_no_issue(self):
        term = _make_term(smiles="CC(=O)O", mass_mono=self._exact_mass)
        assert self.rule.check(term) == []

    def test_mismatched_mass_mono_raises_error(self):
        term = _make_term(smiles="CC(=O)O", mass_mono=self._exact_mass + 1.0)
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR
        assert issues[0].category == "mass"
        assert "MassMono mismatch" in issues[0].message

    def test_mismatched_mass_has_fix(self):
        term = _make_term(smiles="CC(=O)O", mass_mono=self._exact_mass + 1.0)
        issues = self.rule.check(term)
        fix = issues[0].fix
        assert fix is not None
        assert fix.xref_key == "MassMono"
        assert fix.mod_id == "MOD:99999"

    def test_matching_formula_no_issue(self):
        term = _make_term(smiles="CC(=O)O", formula=self._psimod_formula)
        assert self.rule.check(term) == []

    def test_mismatched_formula_raises_error(self):
        term = _make_term(smiles="CC(=O)O", formula="C 3 H 6 O 2")
        issues = self.rule.check(term)
        assert any(i.category == "mass" and "Formula mismatch" in i.message for i in issues)

    def test_mismatched_formula_has_fix(self):
        term = _make_term(smiles="CC(=O)O", formula="C 3 H 6 O 2")
        issues = self.rule.check(term)
        mass_issues = [i for i in issues if "Formula mismatch" in i.message]
        assert mass_issues[0].fix is not None
        assert mass_issues[0].fix.xref_key == "Formula"

    def test_custom_tolerance_accepted(self):
        loose_rule = MassConsistencyRule(tolerance_da=5.0)
        term = _make_term(smiles="CC(=O)O", mass_mono=self._exact_mass + 1.0)
        assert loose_rule.check(term) == []

    def test_within_default_tolerance_no_issue(self):
        # Shift well within default 0.01 Da tolerance
        term = _make_term(smiles="CC(=O)O", mass_mono=self._exact_mass + 0.005)
        assert self.rule.check(term) == []


# ---------------------------------------------------------------------------
# _parse_formula_to_dict
# ---------------------------------------------------------------------------


class TestParseFormulaToDictfunction:
    def test_psimod_spaced_format(self):
        result = _parse_formula_to_dict("C 3 H 7 N 1 O 2")
        assert result == {"C": 3, "H": 7, "N": 1, "O": 2}

    def test_compact_format(self):
        result = _parse_formula_to_dict("C3H7NO2")
        assert result == {"C": 3, "H": 7, "N": 1, "O": 2}

    def test_single_atom_no_count(self):
        # "N" alone means count 1 in compact format
        result = _parse_formula_to_dict("N")
        assert result["N"] == 1

    def test_negative_count_spaced(self):
        result = _parse_formula_to_dict("H -1 N 0")
        assert result["H"] == -1
        assert result["N"] == 0


# ---------------------------------------------------------------------------
# _formulas_match
# ---------------------------------------------------------------------------


class TestFormulasMatch:
    def test_same_compact(self):
        assert _formulas_match("C2H4O2", "C2H4O2")

    def test_compact_vs_spaced(self):
        assert _formulas_match("C2H4O2", "C 2 H 4 O 2")

    def test_different_formulas(self):
        assert not _formulas_match("C2H4O2", "C3H6O2")

    def test_different_element_counts(self):
        assert not _formulas_match("C2H4O2", "C2H5O2")


# ---------------------------------------------------------------------------
# _to_psimod_formula
# ---------------------------------------------------------------------------


class TestToPsimodFormula:
    def test_compact_to_spaced(self):
        result = _to_psimod_formula("C2H4O2")
        assert result == "C 2 H 4 O 2"

    def test_alphabetical_order(self):
        # Elements should be sorted alphabetically
        result = _to_psimod_formula("H4C2O2")
        parts = result.split()
        elements = parts[::2]  # every other token is an element
        assert elements == sorted(elements)
