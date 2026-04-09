// Explicit Commitment Debt (ECD) — Rust reference implementation.
//
// A trace-level audit primitive for human-in-the-loop multi-agent decision systems.
// The load-bearing safety property is enforced both at runtime AND at compile time:
// the `DeterministicVerification` token can only be constructed by an authorized
// module (in production, gated behind a thalamus / verifier crate). Attempts to
// silently resolve a claim with a soft verification fail to compile.
//
// Prior art (cite all of these in any derivative work):
//   - Singh, M. P. (2000). An ontology for commitments in multiagent systems. AI and Law 7(1).
//   - Yolum & Singh (2002). Commitment Machines. ATAL 2001, Springer LNCS 2333.
//   - Klyubin, Polani & Nehaniv (2005). Empowerment.
//   - Kulveit et al. (2025). Gradual Disempowerment. ICML 2025. arXiv:2501.16946.
//
// The ledger rule (NOT a conservation law in the physics sense):
//   - D is monotone-increasing under governance.
//   - D can only decrease via a CONFIRMED deterministic verification event.
//   - DENIED leaves D unchanged but triggers a hard reset of an earned-autonomy
//     trust streak elsewhere in the system. That counter is SEPARATE from D.
//
// Cargo dependencies (add to Cargo.toml):
//   uuid = { version = "1", features = ["v4"] }
//   chrono = { version = "0.4", features = ["serde"] }
//
// License: MIT

use chrono::Utc;
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum VerificationStatus {
    Confirmed,
    Denied,
}

/// Proof that a deterministic verification event occurred.
///
/// In production, this struct's constructor should be `pub(crate)` and only
/// the thalamus / verifier module should be able to construct it. That makes
/// silent inference a compile-time error: callers cannot fabricate this token
/// without going through the verifier.
///
/// In this reference implementation `new` is `pub` for testability — replace
/// with `pub(crate)` in your fork to enforce the privacy invariant.
#[derive(Debug, Clone)]
pub struct DeterministicVerification {
    status: VerificationStatus,
    evidence: String,
    verified_at: String,
}

impl DeterministicVerification {
    pub fn new(status: VerificationStatus, evidence: String) -> Self {
        DeterministicVerification {
            status,
            evidence,
            verified_at: Utc::now().to_rfc3339(),
        }
    }

    pub fn status(&self) -> &VerificationStatus {
        &self.status
    }

    pub fn evidence(&self) -> &str {
        &self.evidence
    }
}

#[derive(Debug, Clone)]
pub enum ClaimStatus {
    Unresolved,
    Resolved {
        verification: DeterministicVerification,
    },
}

#[derive(Debug, Clone)]
pub struct Claim {
    pub id: String,
    pub text: String,
    pub author_id: String,
    pub authored_at: String,
    pub weight: f64,
    pub status: ClaimStatus,
}

#[derive(Debug)]
pub enum EcdError {
    ClaimNotFound(String),
    AlreadyResolved(String),
}

impl std::fmt::Display for EcdError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EcdError::ClaimNotFound(id) => write!(f, "Claim {} not found", id),
            EcdError::AlreadyResolved(id) => write!(f, "Claim {} already resolved", id),
        }
    }
}

impl std::error::Error for EcdError {}

pub struct ExplicitCommitmentDebt {
    claims: HashMap<String, Claim>,
    insertion_order: Vec<String>,
    total_debt: f64,
}

impl Default for ExplicitCommitmentDebt {
    fn default() -> Self {
        Self::new()
    }
}

impl ExplicitCommitmentDebt {
    pub fn new() -> Self {
        ExplicitCommitmentDebt {
            claims: HashMap::new(),
            insertion_order: Vec::new(),
            total_debt: 0.0,
        }
    }

    /// Register a new explicit claim from a human. Increments D by `weight`.
    pub fn add_claim(&mut self, text: String, author_id: String, weight: f64) -> String {
        let id = format!("claim-{}", uuid::Uuid::new_v4());
        let claim = Claim {
            id: id.clone(),
            text,
            author_id,
            authored_at: Utc::now().to_rfc3339(),
            weight,
            status: ClaimStatus::Unresolved,
        };
        self.total_debt += weight;
        self.claims.insert(id.clone(), claim);
        self.insertion_order.push(id.clone());
        id
    }

    /// Resolve a claim using a deterministic verification token.
    ///
    /// The load-bearing safety property: this function takes a
    /// `DeterministicVerification` by value, which can only be constructed by
    /// the verifier module. Soft verifications cannot reach this function
    /// because they cannot be expressed in the type system.
    pub fn resolve_claim(
        &mut self,
        claim_id: &str,
        verification: DeterministicVerification,
    ) -> Result<(String, f64), EcdError> {
        let claim = self
            .claims
            .get_mut(claim_id)
            .ok_or_else(|| EcdError::ClaimNotFound(claim_id.to_string()))?;

        match &claim.status {
            ClaimStatus::Resolved { .. } => {
                Err(EcdError::AlreadyResolved(claim_id.to_string()))
            }
            ClaimStatus::Unresolved => {
                if matches!(verification.status, VerificationStatus::Confirmed) {
                    self.total_debt -= claim.weight;
                }
                // If Denied: D stays the same. The earned-autonomy trust streak
                // (a SEPARATE counter, not in this struct) hard-resets to zero.
                claim.status = ClaimStatus::Resolved { verification };
                Ok((claim_id.to_string(), self.total_debt))
            }
        }
    }

    /// Query the current ECD state. Returns `(total_debt, unresolved_count)`.
    pub fn get_debt(&self) -> (f64, usize) {
        let unresolved = self
            .claims
            .values()
            .filter(|c| matches!(c.status, ClaimStatus::Unresolved))
            .count();
        (self.total_debt, unresolved)
    }

    /// Export the full claim trace for audit, in insertion order.
    pub fn get_trace(&self) -> Vec<&Claim> {
        self.insertion_order
            .iter()
            .filter_map(|id| self.claims.get(id))
            .collect()
    }
}
