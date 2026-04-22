"""Tests for PsiModValidator integration (load OBO → run rules → report)."""

import pytest

from psimod_validator._rules.smiles import SmilesParseRule
from psimod_validator.models import Severity, ValidationReport
from psimod_validator.validator import PsiModValidator


class TestPsiModValidatorInit:
    def test_loads_valid_obo(self, obo_path):
        v = PsiModValidator(obo_path)
        assert v.ontology is not None

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            PsiModValidator(tmp_path / "nonexistent.obo")

    def test_default_rules_populated(self, obo_path):
        v = PsiModValidator(obo_path)
        assert len(v.rules) > 0

    def test_custom_rules_used(self, obo_path):
        rule = SmilesParseRule()
        v = PsiModValidator(obo_path, rules=[rule])
        assert v.rules == [rule]


class TestValidateAll:
    def test_returns_validation_report(self, obo_path):
        report = PsiModValidator(obo_path).validate_all()
        assert isinstance(report, ValidationReport)

    def test_obsolete_terms_excluded(self, obo_path):
        # Fixture has 4 non-obsolete terms (MOD:00000-00003) and 1 obsolete (MOD:00004)
        report = PsiModValidator(obo_path).validate_all()
        assert report.total_terms == 4

    def test_invalid_smiles_produces_error(self, obo_path):
        # MOD:00003 has an unparseable SMILES — expect a parse error
        report = PsiModValidator(obo_path).validate_all()
        smiles_errors = [
            i for i in report.errors if i.mod_id == "MOD:00003" and i.category == "smiles"
        ]
        assert len(smiles_errors) >= 1

    def test_valid_smiles_no_parse_error(self, obo_path):
        report = PsiModValidator(obo_path).validate_all()
        parse_errors = [
            i for i in report.errors if i.mod_id == "MOD:00001" and "cannot parse" in i.message
        ]
        assert parse_errors == []


class TestValidateTerm:
    def test_known_term_returns_list(self, obo_path):
        v = PsiModValidator(obo_path)
        issues = v.validate_term("MOD:00001")
        assert isinstance(issues, list)

    def test_unknown_term_returns_existence_error(self, obo_path):
        v = PsiModValidator(obo_path)
        issues = v.validate_term("MOD:99999")
        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR
        assert issues[0].category == "existence"

    def test_bad_smiles_term_has_parse_error(self, obo_path):
        v = PsiModValidator(obo_path)
        issues = v.validate_term("MOD:00003")
        parse_errors = [i for i in issues if "cannot parse" in i.message]
        assert len(parse_errors) == 1
