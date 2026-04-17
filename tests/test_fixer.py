"""Tests for apply_fixes(), write_obo(), and FixReport."""

from pronto import Ontology

from psimod_validator.fixer import FixReport, apply_fixes, write_obo
from psimod_validator.models import Fix, Issue, Severity


def _fix(mod_id="MOD:00001", xref_key="SMILES", new_value="*NC(C)C(*)=O") -> Fix:
    return Fix(mod_id=mod_id, xref_key=xref_key, old_value=None, new_value=new_value, reason="test")


def _issue_with_fix(**kwargs) -> Issue:
    return Issue(
        severity=Severity.WARNING,
        mod_id=kwargs.get("mod_id", "MOD:00001"),
        category="smiles",
        message="test issue",
        fix=_fix(**kwargs),
    )


# ---------------------------------------------------------------------------
# FixReport
# ---------------------------------------------------------------------------

class TestFixReport:
    def test_applied_count(self):
        report = FixReport(applied=[_fix(), _fix()])
        assert report.applied_count == 2

    def test_skipped_count(self):
        report = FixReport(skipped=[(_fix(), "reason")])
        assert report.skipped_count == 1

    def test_empty_report(self):
        report = FixReport()
        assert report.applied_count == 0
        assert report.skipped_count == 0


# ---------------------------------------------------------------------------
# apply_fixes
# ---------------------------------------------------------------------------

class TestApplyFixes:
    def test_empty_issues_no_changes(self, fresh_ontology):
        report = apply_fixes(fresh_ontology, [])
        assert report.applied_count == 0
        assert report.skipped_count == 0

    def test_issue_without_fix_ignored(self, fresh_ontology):
        issue = Issue(Severity.WARNING, "MOD:00001", "smiles", "no fix here")
        report = apply_fixes(fresh_ontology, [issue])
        assert report.applied_count == 0

    def test_unknown_term_skipped(self, fresh_ontology):
        issue = _issue_with_fix(mod_id="MOD:99999")
        report = apply_fixes(fresh_ontology, [issue])
        assert report.applied_count == 0
        assert report.skipped_count == 1

    def test_replaces_existing_xref(self, fresh_ontology):
        # MOD:00001 has SMILES: "*N[C@@H](C)C(*)=O" — update it
        new_smiles = "*NC(C)C(*)=O"
        issue = _issue_with_fix(mod_id="MOD:00001", xref_key="SMILES", new_value=new_smiles)
        report = apply_fixes(fresh_ontology, [issue])

        assert report.applied_count == 1
        term = fresh_ontology["MOD:00001"]
        smiles_xref = next((x for x in term.xrefs if x.id == "SMILES:"), None)
        assert smiles_xref is not None
        assert smiles_xref.description == new_smiles

    def test_adds_new_xref_when_absent(self, fresh_ontology):
        # MOD:00001 has no MassAvg xref set — actually it does in fixture, use a novel key
        # MOD:00003 has only SMILES — add a Formula xref that doesn't exist
        issue = _issue_with_fix(mod_id="MOD:00003", xref_key="Formula", new_value="C 3 H 5 N 1 O 1")
        report = apply_fixes(fresh_ontology, [issue])

        assert report.applied_count == 1
        term = fresh_ontology["MOD:00003"]
        formula_xref = next((x for x in term.xrefs if x.id == "Formula:"), None)
        assert formula_xref is not None
        assert formula_xref.description == "C 3 H 5 N 1 O 1"

    def test_existing_unrelated_xrefs_preserved(self, fresh_ontology):
        # Apply a SMILES fix on MOD:00001 and verify Origin xref is still there
        issue = _issue_with_fix(mod_id="MOD:00001", xref_key="SMILES", new_value="*NC(C)C(*)=O")
        apply_fixes(fresh_ontology, [issue])

        term = fresh_ontology["MOD:00001"]
        origin_xref = next((x for x in term.xrefs if x.id == "Origin:"), None)
        assert origin_xref is not None
        assert origin_xref.description == "A"


# ---------------------------------------------------------------------------
# write_obo
# ---------------------------------------------------------------------------

class TestWriteObo:
    def test_writes_valid_obo(self, fresh_ontology, tmp_path):
        out = tmp_path / "output.obo"
        write_obo(fresh_ontology, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_written_file_reloadable(self, fresh_ontology, tmp_path):
        out = tmp_path / "output.obo"
        write_obo(fresh_ontology, out)
        reloaded = Ontology(str(out))
        assert "MOD:00001" in [t.id for t in reloaded.terms()]

    def test_fix_persisted_after_write_and_reload(self, fresh_ontology, tmp_path):
        new_smiles = "*NC(C)C(*)=O"
        issue = _issue_with_fix(mod_id="MOD:00001", xref_key="SMILES", new_value=new_smiles)
        apply_fixes(fresh_ontology, [issue])

        out = tmp_path / "fixed.obo"
        write_obo(fresh_ontology, out)
        reloaded = Ontology(str(out))

        term = reloaded["MOD:00001"]
        smiles_xref = next((x for x in term.xrefs if x.id == "SMILES:"), None)
        assert smiles_xref is not None
        assert smiles_xref.description == new_smiles
