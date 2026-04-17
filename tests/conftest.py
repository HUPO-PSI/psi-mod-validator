"""Shared test fixtures for psimod-validator tests."""

import pytest
from pronto import Ontology

# Minimal PSI-MOD-style OBO used across multiple test modules.
# Uses the same xref conventions as real PSI-MOD: annotation keys are stored as
# Xref(id='KEY:', description='value'), and uniprot.ptm as Xref(id='uniprot.ptm:ID').
_OBO_BYTES = b"""\
format-version: 1.2
ontology: psi-mod-test

[Term]
id: MOD:00000
name: protein modification
def: "Root term for all modifications." []

[Term]
id: MOD:00001
name: L-alanine residue
def: "An alanine residue in a peptide chain." [PubMed:12345]
is_a: MOD:00000
xref: SMILES: "*N[C@@H](C)C(*)=O"
xref: Formula: "C 3 H 5 N 1 O 1"
xref: MassMono: "71.037114"
xref: MassAvg: "71.079"
xref: DiffMono: "-0.984016"
xref: DiffAvg: "-0.921"
xref: DiffFormula: "H -1"
xref: Origin: "A"
xref: Source: "natural"
xref: TermSpec: "none"
xref: Unimod: "Unimod:7"
xref: uniprot.ptm:PTM-0118

[Term]
id: MOD:00002
name: charged modification
def: "A positively charged modification." []
is_a: MOD:00000
xref: SMILES: "[NH3+]CC(=O)O"
xref: FormalCharge: "1+"

[Term]
id: MOD:00003
name: bad smiles term
def: "A term carrying an unparseable SMILES." []
is_a: MOD:00000
xref: SMILES: "invalid_smiles_xyz"

[Term]
id: MOD:00004
name: obsolete term
is_obsolete: true
"""


@pytest.fixture(scope="session")
def obo_path(tmp_path_factory):
    """Path to a temporary OBO file. Read-only — do not mutate the ontology."""
    p = tmp_path_factory.mktemp("obo") / "test.obo"
    p.write_bytes(_OBO_BYTES)
    return p


@pytest.fixture
def fresh_ontology(tmp_path):
    """Fresh Ontology instance per test — safe to mutate (used by fixer tests)."""
    p = tmp_path / "test.obo"
    p.write_bytes(_OBO_BYTES)
    return Ontology(str(p))


@pytest.fixture(scope="session")
def ontology(obo_path):
    """Session-scoped read-only ontology."""
    return Ontology(str(obo_path))
