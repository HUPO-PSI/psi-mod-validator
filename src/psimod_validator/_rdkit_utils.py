"""RDKit utilities for SMILES parsing, validation, and structural analysis.

All structural operations go through RDKit molecule objects — no string
manipulation on SMILES strings.
"""

from __future__ import annotations

from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors

# Suppress RDKit warnings during parsing (we handle errors ourselves)
_logger = RDLogger.logger()
_logger.setLevel(RDLogger.ERROR)

# ---------------------------------------------------------------------------
# Pre-compiled SMARTS patterns for backbone detection
# ---------------------------------------------------------------------------

# Dummy atom (atomic number 0) bonded to nitrogen — N-terminal connection
_N_TERMINAL_SMARTS = Chem.MolFromSmarts("[#0]~[#7]")

# Carbon bonded to dummy atom with double-bond to oxygen — C-terminal connection
_C_TERMINAL_SMARTS = Chem.MolFromSmarts("[#6](~[#0])=O")

# Any dummy atom
_DUMMY_ATOM_SMARTS = Chem.MolFromSmarts("[#0]")


def parse_smiles(smiles: str) -> Chem.Mol | None:
    """Parse a SMILES string into an RDKit Mol object.

    Parameters
    ----------
    smiles
        SMILES string to parse

    Returns
    -------
    Chem.Mol or None
        Parsed molecule, or None if invalid

    """
    if not smiles or not smiles.strip():
        return None
    return Chem.MolFromSmiles(smiles, sanitize=True)


def canonicalize(mol: Chem.Mol) -> str:
    """Convert molecule to canonical SMILES, preserving stereochemistry.

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    str
        Canonical SMILES string

    """
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def is_canonical(smiles: str, mol: Chem.Mol) -> bool:
    """Check if a SMILES string is already in canonical form.

    Parameters
    ----------
    smiles
        Original SMILES string
    mol
        Parsed molecule from the same SMILES

    Returns
    -------
    bool
        True if the SMILES is already canonical

    """
    return smiles == canonicalize(mol)


# ---------------------------------------------------------------------------
# Dummy atom / backbone analysis
# ---------------------------------------------------------------------------


def count_dummy_atoms(mol: Chem.Mol) -> int:
    """Count dummy atoms (atom number 0) in a molecule.

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    int
        Number of dummy atoms

    """
    return len(mol.GetSubstructMatches(_DUMMY_ATOM_SMARTS))


def has_n_terminal_dummy(mol: Chem.Mol) -> bool:
    """Check for N-terminal backbone connection (dummy-N bond).

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    bool
        True if a dummy atom bonded to nitrogen is present

    """
    return mol.HasSubstructMatch(_N_TERMINAL_SMARTS)


def has_c_terminal_dummy(mol: Chem.Mol) -> bool:
    """Check for C-terminal backbone connection (C(-dummy)=O pattern).

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    bool
        True if a C-terminal dummy pattern is present

    """
    return mol.HasSubstructMatch(_C_TERMINAL_SMARTS)


# ---------------------------------------------------------------------------
# Chemical property checks
# ---------------------------------------------------------------------------


def get_formal_charge(mol: Chem.Mol) -> int:
    """Get the net formal charge of a molecule.

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    int
        Net formal charge

    """
    return Chem.GetFormalCharge(mol)


def check_valence(mol: Chem.Mol) -> list[str]:
    """Check for valence errors in a molecule.

    Parameters
    ----------
    mol
        RDKit Mol object (already sanitized on parse)

    Returns
    -------
    list[str]
        List of valence problem descriptions (empty if OK)

    """
    problems: list[str] = []
    try:
        Chem.SanitizeMol(
            mol,
            sanitizeOps=Chem.SanitizeFlags.SANITIZE_PROPERTIES,
        )
    except Chem.AtomValenceException as e:
        problems.append(str(e))
    except Exception as e:
        problems.append(f"Valence check error: {e}")
    return problems


def find_undefined_stereocenters(mol: Chem.Mol) -> list[int]:
    """Find stereocenters without defined stereochemistry.

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    list[int]
        Atom indices of undefined stereocenters

    """
    undefined = []
    chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    for idx, chirality in chiral_centers:
        if chirality == "?":
            undefined.append(idx)
    return undefined


def get_molecular_formula(mol: Chem.Mol) -> str:
    """Get molecular formula from a molecule.

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    str
        Molecular formula (e.g., "C3H7NO2")

    """
    return rdMolDescriptors.CalcMolFormula(mol)


def get_exact_mass(mol: Chem.Mol) -> float:
    """Get exact (monoisotopic) mass of a molecule.

    Parameters
    ----------
    mol
        RDKit Mol object

    Returns
    -------
    float
        Monoisotopic mass in Daltons

    """
    return rdMolDescriptors.CalcExactMolWt(mol)
