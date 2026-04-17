"""Cross-reference validation rules.

Validates format and optionally checks online existence of external
database cross-references (Unimod, ChEBI, RESID, UniProt PTM).
"""

from __future__ import annotations

import logging
import re

import requests

from psimod_validator._term_data import TermData
from psimod_validator.models import Issue, Severity

LOGGER = logging.getLogger(__name__)

# Pattern for a single Origin token: uppercase letter or MOD accession
_ORIGIN_TOKEN = re.compile(r"^([A-Z]|MOD:\d{5,6}|none)$")


def _is_valid_origin(origin: str) -> bool:
    """Check if an Origin string is valid.

    Accepts single letters, MOD accessions, "none", or comma-separated
    combinations (e.g., "K", "K, K, K", "MOD:00030", "H, MOD:00030").
    """
    return all(_ORIGIN_TOKEN.match(token.strip()) for token in origin.split(","))


class XrefFormatRule:
    """Validate format of cross-reference annotations."""

    category = "xref"

    def check(self, term: TermData) -> list[Issue]:
        issues: list[Issue] = []

        # Validate Unimod ID format (should be numeric)
        if term.unimod_id is not None and not term.unimod_id.isdigit():
            issues.append(
                Issue(
                    severity=Severity.ERROR,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=f"Invalid Unimod ID format: {term.unimod_id!r}",
                )
            )

        # Validate UniProt PTM format (PTM-XXXX)
        if term.uniprot_ptm is not None and not re.match(r"^PTM-\d{4}$", term.uniprot_ptm):
            issues.append(
                Issue(
                    severity=Severity.ERROR,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=f"Invalid UniProt PTM format: {term.uniprot_ptm!r}",
                )
            )

        # Validate Origin: comma-separated list of single letters, MOD accessions, or "none"
        # e.g., "K", "K, K, K", "MOD:00030", "H, MOD:00030", "none"
        if term.origin is not None and not _is_valid_origin(term.origin):
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=f"Invalid Origin format: {term.origin!r}",
                )
            )

        return issues


class XrefOnlineRule:
    """Verify cross-references exist in external databases via HTTP.

    Only instantiated when --check-online is specified.
    """

    category = "xref"

    def __init__(self, *, timeout: int = 10) -> None:
        self.timeout = timeout
        self._session = requests.Session()

    def check(self, term: TermData) -> list[Issue]:
        issues: list[Issue] = []

        if (
            term.unimod_id is not None
            and term.unimod_id.isdigit()
            and not self._check_unimod(term.unimod_id)
        ):
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    mod_id=term.mod_id,
                    category=self.category,
                    message=f"Unimod:{term.unimod_id} not found online",
                )
            )

        return issues

    def _check_unimod(self, unimod_id: str) -> bool:
        """Check if a Unimod ID exists online."""
        url = f"http://www.unimod.org/modifications_view.php?editid1={unimod_id}"
        try:
            response = self._session.head(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )
            return response.status_code == 200
        except requests.RequestException:
            LOGGER.debug("Failed to check Unimod:%s online", unimod_id)
            return False
