"""Tests for validation rules."""

from psimod_validator._rdkit_utils import parse_smiles
from psimod_validator._rules.backbone import BackbonePatternRule, TermSpecConsistencyRule
from psimod_validator._rules.charge import FormalChargeRule
from psimod_validator._rules.smiles import (
    SmilesCanonicalRule,
    SmilesParseRule,
    SmilesStereochemistryRule,
)
from psimod_validator._rules.structure import TermHierarchyRule, TermNameRule
from psimod_validator._rules.xref import XrefFormatRule
from psimod_validator._term_data import TermData
from psimod_validator.models import Severity


def _make_term(**kwargs) -> TermData:
    """Create a TermData with defaults for testing."""
    defaults = {
        "mod_id": "MOD:99999",
        "name": "test term",
        "definition": "A test term.",
        "is_obsolete": False,
    }
    defaults.update(kwargs)
    # Parse mol from smiles if provided
    if "smiles" in defaults and defaults["smiles"] is not None and "mol" not in defaults:
        defaults["mol"] = parse_smiles(defaults["smiles"])
    return TermData(**defaults)


class TestSmilesParseRule:
    rule = SmilesParseRule()

    def test_no_smiles_no_issue(self):
        term = _make_term()
        assert self.rule.check(term) == []

    def test_valid_smiles(self):
        term = _make_term(smiles="CC(=O)O")
        assert self.rule.check(term) == []

    def test_invalid_smiles(self):
        term = _make_term(smiles="invalid", mol=None)
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR


class TestSmilesCanonicalRule:
    rule = SmilesCanonicalRule()

    def test_canonical_no_issue(self):
        term = _make_term(smiles="CC(=O)O")
        assert self.rule.check(term) == []

    def test_non_canonical_has_fix(self):
        # OC(C)=O is non-canonical form of CC(=O)O
        smiles = "OC(C)=O"
        mol = parse_smiles(smiles)
        term = _make_term(smiles=smiles, mol=mol)
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert issues[0].severity == Severity.WARNING
        assert issues[0].fix is not None
        assert issues[0].fix.new_value == "CC(=O)O"


class TestSmilesStereochemistryRule:
    rule = SmilesStereochemistryRule()

    def test_defined_stereo_no_issue(self):
        term = _make_term(smiles="C[C@H](N)C(=O)O")
        assert self.rule.check(term) == []

    def test_undefined_stereo_warning(self):
        term = _make_term(smiles="CC(N)C(=O)O")
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert issues[0].severity == Severity.WARNING


class TestBackbonePatternRule:
    rule = BackbonePatternRule()

    def test_standard_backbone(self):
        term = _make_term(smiles="*NC(C)C(*)=O")
        assert self.rule.check(term) == []

    def test_no_dummy_no_issue(self):
        term = _make_term(smiles="CC(=O)O")
        assert self.rule.check(term) == []

    def test_too_many_dummies(self):
        term = _make_term(smiles="*NC(*)C(*)=O")
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert "Unusual number" in issues[0].message


class TestTermSpecConsistencyRule:
    rule = TermSpecConsistencyRule()

    def test_no_term_spec_no_issue(self):
        term = _make_term(smiles="*NC(C)C(*)=O", term_spec="none")
        assert self.rule.check(term) == []

    def test_consistent_side_chain(self):
        term = _make_term(smiles="*NC(C)C(*)=O", term_spec="side-chain")
        assert self.rule.check(term) == []


class TestFormalChargeRule:
    rule = FormalChargeRule()

    def test_neutral_no_annotation(self):
        term = _make_term(smiles="CC(=O)O")
        assert self.rule.check(term) == []

    def test_charged_missing_annotation(self):
        term = _make_term(smiles="[NH3+]CC(=O)O")
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert issues[0].fix is not None

    def test_charge_matches(self):
        term = _make_term(smiles="[NH3+]CC(=O)O", formal_charge=1)
        assert self.rule.check(term) == []


class TestXrefFormatRule:
    rule = XrefFormatRule()

    def test_valid_unimod(self):
        term = _make_term(unimod_id="375", def_xrefs=["Unimod:375"])
        assert self.rule.check(term) == []

    def test_invalid_unimod(self):
        term = _make_term(unimod_id="abc")
        issues = self.rule.check(term)
        assert any("Invalid Unimod" in i.message for i in issues)

    def test_valid_origin(self):
        term = _make_term(origin="K")
        assert self.rule.check(term) == []


class TestTermNameRule:
    rule = TermNameRule()

    def test_has_name(self):
        term = _make_term(name="L-alanine residue")
        assert self.rule.check(term) == []

    def test_missing_name(self):
        term = _make_term(name=None)
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR


class TestTermHierarchyRule:
    rule = TermHierarchyRule()

    def test_root_term_no_issue(self):
        term = _make_term(mod_id="MOD:00000")
        assert self.rule.check(term) == []

    def test_has_parent(self):
        term = _make_term(superclass_ids=["MOD:00001"])
        assert self.rule.check(term) == []

    def test_no_parent_warning(self):
        term = _make_term()
        issues = self.rule.check(term)
        assert len(issues) == 1
        assert issues[0].severity == Severity.WARNING
