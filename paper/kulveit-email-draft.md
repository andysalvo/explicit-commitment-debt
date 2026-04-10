# Email draft to Jan Kulveit

**Status:** Draft. Do not send until Paper 1 is on arXiv. The paper draft is at `paper/ecd-paper-v1.md`. The arXiv submission is the prerequisite — the email needs a link the recipient can verify.

**Recipient:** Jan Kulveit (lead author of *Gradual Disempowerment*, ICML 2025; arXiv:2501.16946)
**Find email at:** ICML 2025 paper PDF, last page; or Kulveit's institutional page; or his Twitter/X bio.
**Subject line:** A pre-registered runtime instrument for gradual disempowerment

---

Dr. Kulveit,

I built a runtime instrument for the gradual disempowerment phenomenon you and your coauthors named at ICML 2025. It is called **Explicit Commitment Debt** (ECD): a 24-line scalar audit primitive that counts unresolved commitments in a decision trace, with a runtime rule that `UNABLE_TO_CHECK` verifications throw rather than silently resolve. The pre-registration is on the OSF at [osf.io/az6r3](https://osf.io/az6r3/), the analysis script is hash-pinned, and the canonical data and results are public at github.com/andysalvo/explicit-commitment-debt.

The first pre-registered test (single-agent `gpt-4.1-mini` on 525 disjoint MBPP problems) returned `INCONCLUSIVE_REPORTED_AS_NEGATIVE` per the pre-registered decision rule, despite a Mann-Whitney U significance of p = 0.000167 in the predicted direction. The decision rule failed at the median floor of zero. The full negative result is in the manuscript at [arXiv link]. I would value your reaction whether the verdict is positive or negative.

The follow-up experiment, which tests architectural rather than behavioral structural role separation on a multi-step agent system, will be a separate pre-registration. I would welcome any thoughts on the instrument or on whether ECD is useful as a measurement layer for the broader gradual-disempowerment research program.

Andy Salvo
Penn State University
github.com/andysalvo

---

## Notes for the author before sending

- **Replace `[arXiv link]`** with the actual arXiv URL once the paper is posted. Do not send the email referencing only the GitHub repo. The email exists to put a peer-reviewable artifact in front of Kulveit; the artifact must be on arXiv (or in a workshop submission) to count.
- **Do not attach the PDF.** Link to arXiv. Researchers do not download PDFs from cold emails by strangers.
- **Do not list the verdict as the headline.** The headline is the *instrument*. The verdict is reported transparently because the rigor argument requires it, but the value to Kulveit is the instrument, not whether the first test of the instrument confirmed the hypothesis.
- **Three sentences per paragraph maximum.** Keep it scannable. Kulveit is a busy ICML author and will read the first sentence of each paragraph to decide whether to keep reading.
- **Do not name-drop other AI labs.** No mention of CORE, no mention of Mentat, no mention of Anthropic or DeepMind. The email is about *his* paper and *your* instrument. Adjacent work is for the manuscript.
- **Follow up exactly once if there is no reply within 7 days.** Use the same email thread, add a single sentence that says "in case the original got buried." Then stop.
- **Do not forward this draft to your assistant or to anyone else for editing before Paper 1 is on arXiv.** The email's value depends on the recipient finding the artifact intact when they click. Premature forwarding risks the draft leaking and arriving in Kulveit's inbox before the paper is live.
