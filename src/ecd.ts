/**
 * Explicit Commitment Debt (ECD) — a trace-level audit primitive
 * for human-in-the-loop multi-agent decision systems.
 *
 * This is the load-bearing TypeScript primitive: 24 lines of core class.
 * The contribution lives in `resolveClaim()`, where the rule
 * "no silent inference" becomes a thrown exception at runtime.
 *
 * Prior art (cite all of these in any derivative work):
 *   - Singh, M. P. (2000). An ontology for commitments in multiagent systems. AI and Law 7(1).
 *   - Yolum & Singh (2002). Commitment Machines. ATAL 2001, Springer LNCS 2333.
 *   - Klyubin, Polani & Nehaniv (2005). Empowerment: a universal agent-centric measure of control.
 *   - Kulveit et al. (2025). Gradual Disempowerment. ICML 2025. arXiv:2501.16946.
 *
 * The ledger rule (NOT a conservation law in the physics sense):
 *   - D is monotone-increasing under governance.
 *   - D can only decrease via a CONFIRMED deterministic verification event.
 *   - DENIED leaves D unchanged but triggers a hard reset of an earned-autonomy trust streak
 *     elsewhere in the system. That counter is SEPARATE from D.
 *   - UNABLE_TO_CHECK throws at runtime — claims cannot be silently resolved.
 *
 * License: MIT
 */

export type ClaimStatus = 'UNRESOLVED' | 'CONFIRMED' | 'DENIED';

export type VerificationStatus = 'CONFIRMED' | 'DENIED' | 'UNABLE_TO_CHECK';

export interface Verification {
  status: VerificationStatus;
  evidence: string;
}

export interface Claim {
  id: string;
  text: string;
  authorId: string;
  authoredAt: string;
  weight: number;
  status: ClaimStatus;
  verifiedAt: string | null;
  evidence: string | null;
}

export interface DebtState {
  totalDebt: number;
  unresolvedCount: number;
}

export interface ResolveResult {
  claimId: string;
  status: ClaimStatus;
  newDebt: number;
}

export class ExplicitCommitmentDebt {
  private claims: Claim[];
  private totalDebt: number;

  constructor() {
    this.claims = [];
    this.totalDebt = 0;
  }

  /**
   * Register a new explicit claim from a human.
   * Increments D by `weight`. Status starts as UNRESOLVED.
   */
  addClaim(claimText: string, authorId: string, weight: number = 1.0): string {
    const claim: Claim = {
      id: `claim-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      text: claimText,
      authorId,
      authoredAt: new Date().toISOString(),
      weight,
      status: 'UNRESOLVED',
      verifiedAt: null,
      evidence: null,
    };
    this.claims.push(claim);
    this.totalDebt += weight;
    return claim.id;
  }

  /**
   * Resolve a claim using a deterministic verification result.
   *
   * The load-bearing rule: an UNABLE_TO_CHECK verification THROWS.
   * This is the line that makes "no silent inference" a runtime error
   * instead of a design principle.
   *
   * @throws Error if the claim is not found, already resolved, or the
   *   verification is non-deterministic (UNABLE_TO_CHECK).
   */
  resolveClaim(claimId: string, verification: Verification): ResolveResult {
    const claim = this.claims.find(c => c.id === claimId);
    if (!claim) {
      throw new Error(`Claim ${claimId} not found`);
    }
    if (claim.status !== 'UNRESOLVED') {
      throw new Error(`Claim ${claimId} already resolved (status=${claim.status})`);
    }

    // The load-bearing rule. Do not soften this without breaking ECD.
    if (verification.status === 'UNABLE_TO_CHECK') {
      throw new Error(
        `Cannot resolve claim ${claimId} with uncertain verification. ` +
        `Evidence: "${verification.evidence}". ` +
        `This violates no-silent-inference: the claim remains UNRESOLVED.`
      );
    }

    claim.verifiedAt = new Date().toISOString();
    claim.evidence = verification.evidence;
    claim.status = verification.status;

    if (verification.status === 'CONFIRMED') {
      this.totalDebt -= claim.weight;
    }
    // If DENIED: D stays the same. The earned-autonomy trust streak (a separate
    // counter, not in this class) hard-resets to zero. They are different variables.

    return { claimId, status: claim.status, newDebt: this.totalDebt };
  }

  /**
   * Query the current ECD state.
   */
  getDebt(): DebtState {
    return {
      totalDebt: this.totalDebt,
      unresolvedCount: this.claims.filter(c => c.status === 'UNRESOLVED').length,
    };
  }

  /**
   * Export the full claim trace for audit. Append-only.
   */
  getTrace(): readonly Claim[] {
    return this.claims.map(c => ({ ...c }));
  }
}
