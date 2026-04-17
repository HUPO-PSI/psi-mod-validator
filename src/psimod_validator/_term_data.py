"""Term data extraction from pronto Term objects.

Single source of truth for reading PSI-MOD OBO term annotations into
typed Python objects. All annotation parsing happens here — rule modules
never touch pronto directly.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

from psimod_validator._rdkit_utils import parse_smiles

if TYPE_CHECKING:
    from pronto.term import Term

LOGGER = logging.getLogger(__name__)

# Known xref keys in PSI-MOD that carry annotation values.
# In pronto, these appear as Xref objects where id='KEY:' (with trailing colon)
# and description='VALUE'.
_ANNOTATION_XREF_KEYS = frozenset(
    {
        "SMILES:",
        "DiffFormula:",
        "DiffMono:",
        "DiffAvg:",
        "Formula:",
        "MassMono:",
        "MassAvg:",
        "FormalCharge:",
        "Origin:",
        "Source:",
        "TermSpec:",
    }
)


class TermData(BaseModel):
    """Extracted, typed data from a PSI-MOD pronto Term.

    Attributes
    ----------
    mod_id
        PSI-MOD accession (e.g., "MOD:00046")
    name
        Human-readable term name
    definition
        Term definition text
    is_obsolete
        Whether this term is marked obsolete
    smiles
        Raw SMILES string from the OBO file (None if absent)
    mol
        Parsed RDKit Mol object (None if SMILES absent or invalid)
    diff_formula
        Difference formula (e.g., "C 0 H 0 N 0 O 0")
    diff_mono
        Monoisotopic difference mass
    diff_avg
        Average difference mass
    formula
        Complete molecular formula (e.g., "C 3 H 5 N 1 O 1")
    mass_mono
        Complete monoisotopic mass
    mass_avg
        Complete average mass
    formal_charge
        Formal charge (parsed from e.g., "1+", "2-")
    origin
        Origin amino acid single-letter code
    source
        Source annotation (e.g., "natural", "none")
    term_spec
        TermSpec annotation (e.g., "none")
    unimod_id
        Unimod accession number as string (e.g., "375"), if present
    uniprot_ptm
        UniProt PTM identifier (e.g., "PTM-0118"), if present
    def_xrefs
        Cross-reference IDs from the definition line
    superclass_ids
        Direct parent MOD IDs (from is_a)
    relationships
        Typed relationships: {relationship_type: [MOD:xxxxx, ...]}

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    mod_id: str
    name: str | None = None
    definition: str | None = None
    is_obsolete: bool = False
    smiles: str | None = None
    mol: Any = None  # Chem.Mol — Any to avoid pydantic schema issues
    diff_formula: str | None = None
    diff_mono: float | None = None
    diff_avg: float | None = None
    formula: str | None = None
    mass_mono: float | None = None
    mass_avg: float | None = None
    formal_charge: int | None = None
    origin: str | None = None
    source: str | None = None
    term_spec: str | None = None
    unimod_id: str | None = None
    uniprot_ptm: str | None = None
    def_xrefs: list[str] = []
    superclass_ids: list[str] = []
    relationships: dict[str, list[str]] = {}


def extract_term_data(term: Term) -> TermData:
    """Extract all relevant data from a pronto Term into a TermData object.

    Parameters
    ----------
    term
        A pronto Term object from a PSI-MOD ontology

    Returns
    -------
    TermData
        Typed, extracted term data

    """
    # Build xref lookup: in pronto, PSI-MOD annotations are Xref objects
    # where id='KEY:' (with trailing colon) and description='VALUE'.
    xref_values: dict[str, str] = {}
    unimod_id: str | None = None
    uniprot_ptm: str | None = None

    if term.xrefs:
        for xref in term.xrefs:
            if xref.id in _ANNOTATION_XREF_KEYS and xref.description is not None:
                # Strip trailing colon from key: "SMILES:" -> "SMILES"
                key = xref.id.rstrip(":")
                xref_values[key] = xref.description
            elif xref.id == "Unimod:" and xref.description:
                # Unimod xref: id='Unimod:', desc='Unimod:375'
                unimod_id = xref.description.removeprefix("Unimod:")
            elif xref.id.startswith("uniprot.ptm:"):
                # UniProt PTM: id='uniprot.ptm:PTM-0118', desc=None
                uniprot_ptm = xref.id.removeprefix("uniprot.ptm:")

    # Parse SMILES to Mol
    smiles = xref_values.get("SMILES")
    mol = parse_smiles(smiles) if smiles else None
    if smiles and mol is None:
        LOGGER.debug("Failed to parse SMILES for %s: %s", term.id, smiles)

    # Parse numeric values
    diff_mono = _parse_float(xref_values.get("DiffMono"))
    diff_avg = _parse_float(xref_values.get("DiffAvg"))
    mass_mono = _parse_float(xref_values.get("MassMono"))
    mass_avg = _parse_float(xref_values.get("MassAvg"))

    # Parse formal charge (e.g., "1+", "2-", "0")
    formal_charge = _parse_charge(xref_values.get("FormalCharge"))

    # Extract definition xrefs
    def_xrefs: list[str] = []
    if term.definition and term.definition.xrefs:
        def_xrefs = [xref.id for xref in term.definition.xrefs]

    # Extract direct superclass IDs
    superclass_ids = [sc.id for sc in term.superclasses(distance=1, with_self=False)]

    # Extract typed relationships
    relationships: dict[str, list[str]] = {}
    for rel_type, related_terms in term.relationships.items():
        relationships[rel_type.id] = [t.id for t in related_terms]

    return TermData(
        mod_id=term.id,
        name=term.name,
        definition=str(term.definition) if term.definition else None,
        is_obsolete=term.obsolete,
        smiles=smiles,
        mol=mol,
        diff_formula=xref_values.get("DiffFormula"),
        diff_mono=diff_mono,
        diff_avg=diff_avg,
        formula=xref_values.get("Formula"),
        mass_mono=mass_mono,
        mass_avg=mass_avg,
        formal_charge=formal_charge,
        origin=xref_values.get("Origin"),
        source=xref_values.get("Source"),
        term_spec=xref_values.get("TermSpec"),
        unimod_id=unimod_id,
        uniprot_ptm=uniprot_ptm,
        def_xrefs=def_xrefs,
        superclass_ids=superclass_ids,
        relationships=relationships,
    )


def _parse_float(value: str | None) -> float | None:
    """Parse a string to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_charge(value: str | None) -> int | None:
    """Parse a PSI-MOD formal charge string (e.g., '1+', '2-', '0').

    Parameters
    ----------
    value
        Charge string from OBO xref

    Returns
    -------
    int or None
        Parsed charge, or None if absent or unparseable

    """
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        if value.endswith("+"):
            return int(value[:-1]) if len(value) > 1 else 1
        if value.endswith("-"):
            return -(int(value[:-1]) if len(value) > 1 else 1)
        return int(value)
    except ValueError:
        LOGGER.debug("Could not parse charge: %r", value)
        return None
