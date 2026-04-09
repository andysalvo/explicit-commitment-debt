"""
Explicit Commitment Debt (ECD) — Python reference implementation.

A trace-level audit primitive for human-in-the-loop multi-agent decision systems.
Designed for research / pymdp interop. The load-bearing rule is enforced in
resolve_claim(): an UNABLE_TO_CHECK verification raises ValueError.

Prior art (cite all of these in any derivative work):
  - Singh, M. P. (2000). An ontology for commitments in multiagent systems. AI and Law 7(1).
  - Yolum & Singh (2002). Commitment Machines. ATAL 2001, Springer LNCS 2333.
  - Klyubin, Polani & Nehaniv (2005). Empowerment: a universal agent-centric measure of control.
  - Kulveit et al. (2025). Gradual Disempowerment. ICML 2025. arXiv:2501.16946.

The ledger rule (NOT a conservation law in the physics sense):
  - D is monotone-increasing under governance.
  - D can only decrease via a CONFIRMED deterministic verification event.
  - DENIED leaves D unchanged but triggers a hard reset of an earned-autonomy
    trust streak elsewhere in the system. That counter is SEPARATE from D.
  - UNABLE_TO_CHECK raises at runtime.

License: MIT
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Literal

ClaimStatus = Literal["UNRESOLVED", "CONFIRMED", "DENIED"]
VerificationStatus = Literal["CONFIRMED", "DENIED", "UNABLE_TO_CHECK"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Claim:
    text: str
    author_id: str
    weight: float = 1.0
    authored_at: str = field(default_factory=_now)
    status: ClaimStatus = "UNRESOLVED"
    verified_at: str | None = None
    evidence: str | None = None
    id: str = field(default_factory=lambda: f"claim-{uuid.uuid4()}")


class ExplicitCommitmentDebt:
    """
    Trace-level audit primitive. D = sum of weights of UNRESOLVED claims.

    D is monotone-increasing under governance: it can only decrease via a
    CONFIRMED deterministic verification event recorded with evidence.
    """

    def __init__(self) -> None:
        self.claims: list[Claim] = []
        self.total_debt: float = 0.0

    def add_claim(self, text: str, author_id: str, weight: float = 1.0) -> str:
        """
        Register a new explicit claim from a human. Increments D by `weight`.
        """
        claim = Claim(text=text, author_id=author_id, weight=weight)
        self.claims.append(claim)
        self.total_debt += weight
        return claim.id

    def resolve_claim(self, claim_id: str, verification: dict) -> dict:
        """
        Resolve a claim using a deterministic verification result.

        The load-bearing rule: UNABLE_TO_CHECK verifications raise. This is the
        line that turns "no silent inference" from a design principle into a
        runtime error.

        Raises:
            ValueError: if the claim is missing, already resolved, or the
                verification is non-deterministic.
        """
        claim = next((c for c in self.claims if c.id == claim_id), None)
        if claim is None:
            raise ValueError(f"Claim {claim_id} not found")
        if claim.status != "UNRESOLVED":
            raise ValueError(f"Claim {claim_id} already resolved (status={claim.status})")

        # The load-bearing rule. Do not soften this without breaking ECD.
        if verification.get("status") == "UNABLE_TO_CHECK":
            raise ValueError(
                f"Cannot resolve {claim_id} with uncertain verification. "
                f"Evidence: '{verification.get('evidence', '')}'. "
                f"This violates no-silent-inference: claim remains UNRESOLVED."
            )

        if verification.get("status") not in ("CONFIRMED", "DENIED"):
            raise ValueError(
                f"Verification status must be CONFIRMED, DENIED, or UNABLE_TO_CHECK; "
                f"got {verification.get('status')!r}"
            )

        claim.verified_at = _now()
        claim.evidence = verification.get("evidence")
        claim.status = verification["status"]  # CONFIRMED or DENIED

        if claim.status == "CONFIRMED":
            self.total_debt -= claim.weight
        # If DENIED: D stays the same. The earned-autonomy trust streak (a
        # separate counter, not in this class) hard-resets to zero.

        return {
            "claim_id": claim_id,
            "status": claim.status,
            "new_debt": self.total_debt,
        }

    def get_debt(self) -> dict:
        """Query the current ECD state."""
        return {
            "total_debt": self.total_debt,
            "unresolved_count": sum(1 for c in self.claims if c.status == "UNRESOLVED"),
        }

    def get_trace(self) -> list[dict]:
        """Export the full claim trace for audit. Append-only."""
        return [asdict(c) for c in self.claims]
