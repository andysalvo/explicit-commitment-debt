# ANNOTATED — Explicit Commitment Debt

A line-by-line walkthrough of the TypeScript primitive in `src/ecd.ts`, the prior art it builds on, and the specific reason this exists as a separate artifact.

## The 24 lines that matter

```typescript
export class ExplicitCommitmentDebt {
  constructor() {
    this.claims = [];        // every human-articulated claim ever logged
    this.totalDebt = 0;      // monotone unless a deterministic verification fires
  }

  addClaim(claimText, authorId, weight = 1.0) {
    const claim = {
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

  resolveClaim(claimId, verification) {
    const claim = this.claims.find(c => c.id === claimId);
    if (!claim) throw new Error(`Claim ${claimId} not found`);
    if (claim.status !== 'UNRESOLVED') throw new Error(`Claim ${claimId} already resolved`);

    // Load-bearing rule: no soft verifications may discharge a claim.
    if (verification.status === 'UNABLE_TO_CHECK') {
      throw new Error(
        `Cannot resolve claim ${claimId} with uncertain verification. ` +
        `Evidence: "${verification.evidence}". ` +
        `This violates no-silent-inference: the claim remains UNRESOLVED.`
      );
    }

    claim.verifiedAt = new Date().toISOString();
    claim.evidence = verification.evidence;
    claim.status = verification.status;   // CONFIRMED or DENIED

    if (verification.status === 'CONFIRMED') {
      this.totalDebt -= claim.weight;
    }
    // If DENIED: D stays the same. The earned-autonomy trust streak (a SEPARATE counter,
    // not part of this class) hard-resets to zero. They are different variables.

    return { claimId, status: claim.status, newDebt: this.totalDebt };
  }
}
```

## What each block actually does

### `addClaim`

A human articulates an explicit statement that is decision-relevant. The class records who said it, when, and the weight. The total debt goes up. The claim's status starts as `UNRESOLVED`. Nothing about this is novel — it is a standard observation log with a typed status field.

### `resolveClaim` — the load-bearing function

This is the only place the implementation does anything that the prior art does not already provide. The relevant lines:

```typescript
if (verification.status === 'UNABLE_TO_CHECK') {
  throw new Error(...);
}
```

That is the entire contribution. **It is the line that turns "no silent inference" — an intent that has appeared in every era of the underlying research program — into a runtime error.** Every previous version of this principle was a design rule, a constitutional invariant, or a guideline. Here it is a thrown exception at the one function where a claim could have been silently resolved.

The rule is asymmetric: a `CONFIRMED` deterministic verification decreases `D`, a `DENIED` deterministic verification leaves `D` unchanged (and is the trigger for an earned-autonomy hard reset elsewhere in the system, *not* in this class), and an `UNABLE_TO_CHECK` verification cannot resolve the claim at all. The asymmetry is the point. The principle "do not silently infer" is not enforceable as long as soft verifications are allowed to discharge claims; it becomes enforceable the moment the function refuses to accept them.

### Why this is not a conservation law

The naming agent's first draft called this a "conservation law." It is not. A conservation law is a statement about a physical quantity that is invariant under a symmetry group (Noether's theorem). `D` is **monotone-increasing under governance**: it can only decrease via per-claim verification events. There is no symmetry group, no Lagrangian, no invariance. **Calling `D` "conserved" is a physics category error that any reviewer who knows physics will catch in 30 seconds**, and it conflates `D` with the *separate* earned-autonomy trust streak counter that hard-resets on `DENIED`. The two counters have different update rules, different reset semantics, and different roles. The internal review caught this and split them; the published artifact uses **"ledger rule"** or **"monotone-increasing under governance"** and never the word "conservation."

## Prior art (the part most papers about scoped contributions get wrong)

### Singh & Yolum, *Commitment Machines* (2000, 2002)

The cardinality of an active-commitments set is the standard formal object in this literature. Singh's commitment ontology has commitments with `CREATE / CANCEL / RELEASE / DISCHARGE` states, debtors and creditors, and protocols for "commitments not yet discharged." **`D = count(UNRESOLVED claims)` is the cardinality of the active-commitments set in a Singh-style commitment protocol where the debtor is the human and the creditor is the governance layer.** Stripped of the application-specific framing, that is what ECD is. Any paper, blog post, or talk that does not cite Singh as backbone prior art is not honest about the work.

### Klyubin, Polani & Nehaniv, *Empowerment* (2005)

Empowerment is the formal scalar quantity for agency in AI: Shannon channel capacity from an agent's actions to its future sensor states, measured in bits. **Empowerment is forward-looking channel capacity**. ECD is **backward-looking verification completeness**. They are different but they surround the same conceptual space. Salge & Polani (2017) proposed maximizing *human* empowerment as the alignment objective — that is the closest published proposal for "preserve human agency as a scalar," and it predates ECD by nine years.

### Kulveit et al., *Gradual Disempowerment* (ICML 2025)

The 2025 ICML paper by Krueger and Duvenaud explicitly calls for *"attempts to protect human influence, to estimate the degree of disempowerment, and to better characterize civilization-scale multi-agent dynamics."* That is the scalar this work attempts to instrument. **The phenomenon name is theirs. The trace-level instrument is what ECD adds to it.** ECD is to gradual disempowerment what `ε` is to differential privacy: a concrete parameter that makes the abstract claim measurable.

### Capability-based security, linear types, audit logs

The implementation pattern (resolve a token only via an authorized capability, throw if the capability is missing) is **capability-based security** — KeyKOS, EROS, seL4, the long lineage of object-capability languages. The "discharge once" semantics is the standard motivation for **linear types**. The append-only history field is a standard **audit log**. None of these are novel by themselves. The narrow novelty is the specific composition: a cardinality scalar over discharged commitments, with a runtime check that refuses to accept soft verifications, applied to LLM-agent decision traces.

## What the published paper must say

The narrow defensible claim, in one paragraph:

> We introduce **Explicit Commitment Debt (ECD)**, a trace-level audit primitive for human-in-the-loop LLM agent governance: a scalar `D = count(UNRESOLVED claims)` that measures how many human-authored claims in a decision trace have not yet been discharged by a deterministic verification event with logged evidence. ECD is an adaptation of Yolum and Singh's commitment-machines semantics (AAMAS 2002) to the claim-resolution traces of modern LLM agent stacks, and it is proposed as one instrument for the measurement need articulated by Kulveit et al.'s *Gradual Disempowerment* (ICML 2025). We give a runtime-checkable type signature in TypeScript, Python, and Rust — the load-bearing rule is that `resolveClaim()` throws on any non-deterministic verification, making "no silent inference" a runtime error rather than a design principle. We validate ECD on 500 decision traces from an existing four-plane agent system and pre-register the prediction that traces produced under enforced plane separation have significantly lower mean `D`. **We do not claim to have discovered a new scalar of agency; we claim to have written a small, auditable primitive that fills a measurement gap inside an existing research program.**

That paragraph survives both an arXiv endorsement review and a hostile reviewer who knows commitment machines and gradual disempowerment. The previous draft did not.

## Empirical pre-registration (target: OSF)

**Hypothesis:** In a multi-LLM agent decision trace, mean `D` is significantly lower under enforced structural plane separation than without it. Specifically, traces produced under a four-plane Intent / Management / Control / Data architecture with runtime boundary enforcement will have at least 50% lower mean `D` than traces produced without plane separation, on the same task distribution.

**Independent variable:** binary (plane separation enforced / not enforced).
**Dependent variable:** mean `D` per task, measured at task completion.
**Sample size:** ≥ 500 traces per condition.
**Statistical test:** Mann-Whitney U on the per-task `D` distributions, two-tailed.
**Decision rule:** reject the null at p < 0.01.
**Analysis script:** committed before the experiment runs (in `tests/`).
**Falsifier:** if the two distributions are statistically indistinguishable, ECD is not measuring the governance property it claims to measure. **The negative result is publishable.**

## The firewall

ECD is a research artifact. It does not have a "Try Now" button. It does not have a landing page with a gradient background. It does not link to any commercial product. The narrow novelty claim survives only because the artifact is positioned as research and cites its prior art aggressively. A commercial wrapper would burn the credibility of the scoped contribution.

This rule was pre-committed in the document that produced this artifact. It is not optional. If the rule is broken, the work loses both its honest framing and its only remaining defensible claim.

## What to read next

- `src/ecd.ts` — the TypeScript primitive
- `src/ecd.py` — the Python implementation (for research / pymdp interop)
- `src/ecd.rs` — the Rust implementation (compile-time enforced)
- `examples/usage.ts` — the five-line usage example
- `examples/violation.ts` — the runtime violation that proves the rule fires
- `tests/ecd.test.ts` — the validation harness
