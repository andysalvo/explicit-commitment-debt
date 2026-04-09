# Explicit Commitment Debt (ECD)

A trace-level audit primitive for human-in-the-loop multi-agent decision systems. Makes "no silent inference" a runtime error instead of a design principle.

> **Pre-registered.** OSF: [osf.io/az6r3](https://osf.io/az6r3/) · timestamped 2026-04-09T21:51:48 UTC · pinned analysis: [`tests/preregistered_analysis.py`](tests/preregistered_analysis.py) at commit `9864233`. The analysis script is frozen and self-hashing; any post-registration modification is detectable.

## What this is

ECD is a scalar `D = count(UNRESOLVED claims)` over a decision trace, where:

- A *claim* is an explicit human-authored statement at a decision moment, with `authorId`, `authoredAt`, and text.
- A claim's `status` is `UNRESOLVED`, `CONFIRMED`, or `DENIED`.
- A claim transitions from `UNRESOLVED` only via a deterministic verification event with logged evidence.
- **`UNABLE_TO_CHECK` verifications throw at runtime.** They cannot resolve a claim. This is the load-bearing rule.

The implementation is a 24-line TypeScript class. Equivalent Python and Rust implementations are in `src/`.

## What this is NOT

**ECD is not a new conserved quantity, and it is not "the scalar of agency," and it does not prevent or measure LLM hallucination.** The prior art and adjacent work for these claims is well-established:

- The cardinality of an active-commitments set is the standard formal object in **commitment machines** (Singh 2000; Yolum & Singh 2002).
- A formal scalar of agency in AI is **empowerment** (Klyubin, Polani & Nehaniv 2005), and **maximizing human empowerment** is the alignment proposal of Salge & Polani 2017.
- The phenomenon ECD attempts to measure is **gradual disempowerment**, named and defined by Kulveit, Douglas, Ammann, Turan, Krueger, and Duvenaud (ICML 2025, [arXiv:2501.16946](https://arxiv.org/abs/2501.16946)).
- A complete constitutional runtime governance framework already exists: **CORE** — the 92-rule, 7-engine system for governing AI coding agents. ECD is not that. ECD is a 24-line primitive that CORE-class systems could embed, not a replacement.
- The closest published conceptual neighbor is the **Deterministic Commitment Layer** proposal (GreaterWrong, 2026) — a generalized commitment-layer architecture for model output authorization. ECD is a specific instance of that family, narrowed to the human-claim resolution side and implemented as a runtime throw.
- **Hallucination prevention happens at generation time**, not at claim resolution time. ECD does not modify model activations, does not block hallucinated outputs, and does not measure hallucination rate. Tools that do operate at the activation layer (e.g., Mentat) are a different technical category. ECD operates on the audit trail after the agent has already produced output.

ECD is a **scoped adaptation**: an asymmetric (human-debtor / governance-creditor) cardinality measure of unresolved commitments, applied to the claim-resolution traces of modern LLM agent stacks, with a runtime-checkable type signature for the "no silent inference" rule.

## What is novel (narrowly)

The narrow gap this fills:

> A claim-level audit primitive for human-in-the-loop LLM agent governance, written down as a **monotone-increasing ledger rule** (not a conservation law in the physics sense), with a **runtime-checkable type signature** that throws on non-deterministic verification, with empirical grounding in an existing multi-month decision trace.

That is the entire claim. It is small. It is defensible. It is implementable today.

## Install and usage

```bash
git clone https://github.com/<your-account>/explicit-commitment-debt.git
cd explicit-commitment-debt
# TypeScript: no dependencies, just import src/ecd.ts
# Python: pip install -e . (no external deps)
# Rust: cargo build (requires uuid + chrono crates)
```

Five-line usage in TypeScript:

```typescript
import { ExplicitCommitmentDebt } from './src/ecd.ts';
const ecd = new ExplicitCommitmentDebt();
const id = ecd.addClaim('Write report to /data/report.csv', 'andy@example.com', 1.0);
const result = ecd.resolveClaim(id, { status: 'CONFIRMED', evidence: 'file exists, 2.5 KB' });
console.log(ecd.getDebt()); // { totalDebt: 0, unresolvedCount: 0 }
```

The corresponding violation that throws at runtime:

```typescript
ecd.resolveClaim(id, { status: 'UNABLE_TO_CHECK', evidence: 'LLM guessed this' });
// throws: "Cannot resolve claim with uncertain verification. This violates no-silent-inference."
```

See `examples/` for runnable versions and `ANNOTATED.md` for the line-by-line walkthrough.

## The ledger rule (not a conservation law)

`D` is a **monotone-increasing ledger under governance**: it can only decrease via per-claim deterministic verification events. A `DENIED` event does *not* clear `D` — it triggers a separate hard-reset of an earned-autonomy trust streak, which is a different counter. Treating `D` and the trust streak as the same quantity is a category error and the word "conservation" is reserved for physical quantities like energy and charge that satisfy actual symmetry-derived conservation laws.

## Empirical prediction (pre-registered)

Pre-registration target: OSF, before any experimental run.

> **Hypothesis:** In a multi-LLM agent decision trace, mean `D` is significantly lower under enforced structural plane separation (Polybrain SRS) than without it.

> **Falsifier:** If `D` distributions are statistically indistinguishable between SRS-enforced and non-SRS traces over 500 runs, ECD is not measuring the governance property it claims to measure. The negative result is publishable.

## Prior art (mandatory citations)

Any paper, blog post, or talk that uses ECD must cite at minimum:

- **Singh, M. P.** (2000). *An ontology for commitments in multiagent systems.* AI and Law 7(1).
- **Yolum, P. & Singh, M. P.** (2002). *Commitment Machines.* In Intelligent Agents VIII (ATAL 2001), Springer LNCS 2333.
- **Klyubin, A. S., Polani, D. & Nehaniv, C. L.** (2005). *Empowerment: a universal agent-centric measure of control.* Proceedings of the 2005 IEEE Congress on Evolutionary Computation.
- **Salge, C. & Polani, D.** (2017). *Empowerment as Replacement for the Three Laws of Robotics.* Frontiers in Robotics and AI 4.
- **Kulveit, J., Douglas, R., Ammann, N., Turan, D., Krueger, D. & Duvenaud, D.** (2025). *Gradual Disempowerment.* ICML 2025. [arXiv:2501.16946](https://arxiv.org/abs/2501.16946).

Strongly recommended (contemporary landscape):

- **CORE — Constitutional Governance Runtime** (GitHub project, 2025). The most direct example of runtime-enforced governance for AI coding agents (92 rules, 7 enforcement engines, INTERPRET → PLAN → GENERATE → VALIDATE → STYLE CHECK → EXECUTE pipeline). ECD is not a competitor — ECD is a primitive that systems like CORE could embed.
- **"Deterministic Commitment Layer"** (GreaterWrong post, 2026). The closest contemporaneous conceptual neighbor: a generalized proposal for commitment-layer architecture in AI governance. ECD is a specific runtime implementation of one slice of that proposal.
- **GAIA** — Governance-First Agency Framework (2025). For "authorization boundaries with explicit escalation paths" in LLM-human B2B negotiation. ECD's `UNABLE_TO_CHECK` throw is conceptually adjacent to GAIA's escalation path; cite if discussing authorization boundaries.

Additional adjacent work referenced in `ANNOTATED.md`:

- Haggard & Chambon (2012) on intentional binding and sense of agency.
- Fischer & Ravizza (1998), *Responsibility and Control*.
- Aghion & Tirole (1997), *Formal and Real Authority in Organizations*.
- Bai et al. (2022), *Constitutional AI: Harmlessness from AI Feedback*.
- AEMA (2026), verifiable multi-agent evaluation framework — for traceable evaluation context.

## License

MIT. See `LICENSE`.

## Contributing

This is a research artifact. Issues and PRs that improve the runtime checks, add language implementations, or strengthen the empirical validation are welcome. PRs that wrap ECD in a commercial product or add a "Try Now" landing page will be closed without comment — see `ANNOTATED.md` for why the firewall exists.
