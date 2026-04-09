# ROADMAP — Explicit Commitment Debt

This document is the scope contract. Anything that violates it should be closed or rejected.

## What we WILL do

1. **Run the experiment.** 500 decision traces per condition (SRS-enforced, non-SRS), Mann-Whitney U on per-trace `D` distributions, two-tailed, decision rule p < 0.01. The pre-registered hypothesis is in `ANNOTATED.md`.
2. **Write the paper.** ~10-15 pages, single track. Position ECD as a scoped adaptation of Singh & Yolum (2002) commitment-machines semantics, instrumenting the gradual-disempowerment phenomenon named by Kulveit et al. (ICML 2025). Cite all mandatory and strongly-recommended works listed in `README.md`. Honest disclaimers about what ECD is not.
3. **Post to arXiv.** `cs.AI` + `cs.MA` cross-list. Get an arXiv endorsement from Kulveit, Krueger, Singh, Millidge, or Christiano (in that contact order). HuggingFace endorsement thread is the fallback.
4. **Submit to a workshop.** Targets: NeurIPS 2026 Technical AI Governance workshop, NeurIPS 2026 SoLaR, ICLR 2027 Pluralistic Alignment, AI Safety Camp 2027. **Not the main track.** A first-author independent researcher with no advisor has near-zero acceptance probability at the main track.

That is the entire scope. Everything else is out of bounds for this artifact.

## What we will NOT do

1. **No full governance framework.** CORE already exists with 92 rules and 7 enforcement engines. ECD is a 24-line primitive that CORE-class systems can embed. We do not compete with CORE.
2. **No hallucination prevention.** Hallucination happens at generation time. Mentat-class activation interventions handle that. ECD operates at claim resolution time and is silent on hallucination.
3. **No multi-agent evaluation framework.** AEMA already exists for that. ECD is for live runtime audit, not testing infrastructure.
4. **No B2B negotiation protocol.** GAIA already exists for that. ECD has no concept of negotiation, escalation tree, or commercial-counterparty role.
5. **No commercial wrapper.** No Stripe link in the README. No "Try Now" landing page. No pricing tier. No "Enterprise Governance Platform" framing. The research artifact and any commercial layer stay behind a hard firewall.
6. **No "ECD measures agency" claim.** Empowerment (Klyubin, Polani & Nehaniv 2005) measures agency via Shannon channel capacity. ECD measures unresolved commitments. They are different things.
7. **No "ECD is a new conserved quantity" claim.** The naming agent originally called it that; the critic correctly identified it as a physics category error. The repo uses "ledger rule" / "monotone-increasing under governance" exclusively. The word "conservation" appears only in `ANNOTATED.md`'s explanation of why we don't use it.
8. **No "no one has built anything like this" claim.** CORE, GAIA, the Deterministic Commitment Layer post, and Singh's commitment machines are all in the same family. ECD's narrow novelty is the runtime-checkable type signature with the throw on `UNABLE_TO_CHECK`. Not the concept.

## Decision rules

- **PRs that violate any of the "will NOT do" items are closed without comment.** This is not optional. The firewall is what makes the narrow novelty defensible.
- **PRs that add language implementations, strengthen the empirical validation, improve the runtime checks, or close prior-art gaps are welcome.**
- **Any rename, pivot, or scope expansion requires explicit unfreeze with rationale.** This rule is borrowed from `INVENTION_FROZEN.md` (2026-01-12), the document where the underlying invention was first frozen.

## Mandatory pre-publication checklist

Before any version of this work is posted publicly (arXiv, blog, LessWrong, etc.):

- [ ] OSF preregistration filed and timestamp captured
- [ ] Empirical experiment run on ≥ 500 traces per condition
- [ ] All mandatory citations present in the manuscript:
  - [ ] Singh (2000)
  - [ ] Yolum & Singh (2002)
  - [ ] Klyubin, Polani & Nehaniv (2005)
  - [ ] Salge & Polani (2017)
  - [ ] Kulveit et al. (2025)
- [ ] All strongly-recommended citations present:
  - [ ] CORE (constitutional governance runtime)
  - [ ] Deterministic Commitment Layer (GreaterWrong 2026)
  - [ ] GAIA (governance-first agency framework)
- [ ] Hallucination disclaimer present in abstract or introduction
- [ ] No "conservation" language in the substantive body
- [ ] `D` and the earned-autonomy trust streak explicitly named as separate counters
- [ ] No commercial framing
- [ ] No "we discovered the scalar of agency" or equivalent overclaim
- [ ] At least one peer reviewer (Kulveit, Krueger, Singh, Millidge, or Christiano) has seen the abstract

## Sunset criteria

If the experiment fails to find a significant difference between SRS-enforced and non-SRS conditions over 500 traces:

- **Publish the negative result.** Negative results are publishable.
- **Do not pivot ECD into something it isn't** to avoid the negative result.
- **Update this ROADMAP** to reflect what was learned.

If after 6 months no external researcher has cited or forked the work:

- **Honest retrospective.** Write a short post explaining what the work attempted and why adoption did not happen.
- **Sunset the artifact** with a final commit. Do not silently abandon it.
