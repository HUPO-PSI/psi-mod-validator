"""Validation rule registry."""

from __future__ import annotations

from psimod_validator._rules.backbone import BackbonePatternRule, TermSpecConsistencyRule
from psimod_validator._rules.base import ValidationRule
from psimod_validator._rules.charge import FormalChargeRule
from psimod_validator._rules.mass import MassConsistencyRule
from psimod_validator._rules.smiles import (
    SmilesCanonicalRule,
    SmilesParseRule,
    SmilesStereochemistryRule,
    SmilesValenceRule,
)
from psimod_validator._rules.structure import (
    TermDefinitionRule,
    TermHierarchyRule,
    TermNameRule,
)
from psimod_validator._rules.xref import XrefFormatRule, XrefOnlineRule


def get_default_rules(*, check_online: bool = False) -> list[ValidationRule]:
    """Return all built-in validation rules in recommended order.

    Parameters
    ----------
    check_online
        Whether to include rules that make HTTP requests

    Returns
    -------
    list[ValidationRule]
        Ordered list of rules to run

    """
    rules: list[ValidationRule] = [
        # SMILES checks (parse first, then detailed checks)
        SmilesParseRule(),
        SmilesCanonicalRule(),
        SmilesValenceRule(),
        SmilesStereochemistryRule(),
        # Backbone / term_spec
        BackbonePatternRule(),
        TermSpecConsistencyRule(),
        # Charge
        FormalChargeRule(),
        # Mass / formula consistency
        MassConsistencyRule(),
        # Cross-references
        XrefFormatRule(),
        # Ontology structure
        TermNameRule(),
        TermDefinitionRule(),
        TermHierarchyRule(),
    ]

    if check_online:
        rules.append(XrefOnlineRule())

    return rules


__all__ = [
    "BackbonePatternRule",
    "FormalChargeRule",
    "MassConsistencyRule",
    "SmilesCanonicalRule",
    "SmilesParseRule",
    "SmilesStereochemistryRule",
    "SmilesValenceRule",
    "TermDefinitionRule",
    "TermHierarchyRule",
    "TermNameRule",
    "TermSpecConsistencyRule",
    "ValidationRule",
    "XrefFormatRule",
    "XrefOnlineRule",
    "get_default_rules",
]
