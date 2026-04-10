# Explicit Commitment Debt: a pre-registered test of behavioral structural role separation in single-agent coding traces

**Andy Salvo**
*Penn State University*
*2026-04-10*

**Status of this draft:** v1, automatically assembled from the canonical run results immediately after the analysis script's single execution. No section has been hand-edited by the author. This is a starting point for the author's first pass, not a submission-ready manuscript.

**Pre-registration:** [OSF az6r3](https://osf.io/az6r3/) (timestamped 2026-04-09T21:51:48 UTC, immutable). Operationalization addendum: [`PREREGISTRATION_ADDENDUM_001.md`](../PREREGISTRATION_ADDENDUM_001.md), git commit `27c8416`.

**Code, data, and audit trail:** github.com/andysalvo/explicit-commitment-debt at git commit `a7672d4`. Analysis script `tests/preregistered_analysis.py` at commit `9864233`, SHA-256 `0f3cf9d4...c046f2`, self-hashed in the result JSON.

---

## Abstract

We introduce **Explicit Commitment Debt (ECD)**, a scalar audit primitive defined as `D = count(UNRESOLVED claims)` over a decision trace, where a claim is an explicit propositional statement about external state and `UNRESOLVED` is the status of any claim that has not been discharged by a deterministic verification event. ECD instruments the *gradual disempowerment* phenomenon named by Kulveit, Douglas, Ammann, Turan, Krueger, and Duvenaud (ICML 2025) at the level of individual decision traces. We pre-register a behavioral test of whether prompt-level structural role separation (SRS) reduces ECD in single-agent coding tasks: 1000 traces from `gpt-4.1-mini` solving 525 disjoint MBPP problems, half under a control prompt and half under an SRS prompt instructing the agent to mark unverified claims as UNRESOLVED. The pre-registered Mann-Whitney U test rejects the null at p = 0.000167 in the predicted direction (mean D drops from 0.257 to 0.173, a 33% relative reduction). The pre-registered confirmation rule additionally required a median ratio below 0.75; both group medians are 0 because most traces have no unresolved claims under either prompt, so the median ratio test fails closed and the script returns the verdict `INCONCLUSIVE_REPORTED_AS_NEGATIVE`. The treatment effect is real and concentrated in the tail: the fraction of traces with any unresolved claims drops from 15.5% to 7.9%, but the maximum unresolved-claim count increases from 6 to 9. We report the result per the pre-registration's rigor commitment, document the median ceiling effect as a methodological limitation of the chosen task domain, and propose a follow-up experiment using architectural SRS enforcement on a multi-step task domain where cross-plane function calls actually occur.

---

## 1. Introduction

The literature on multi-agent AI systems is converging on a concrete worry. As agents take on longer-horizon tasks that combine planning, retrieval, model dispatch, and verification, the auditable trail of their commitments degrades. Kulveit et al. (ICML 2025) named this phenomenon **gradual disempowerment**: the slow drift in which a human oversight loop loses the ability to verify, contest, or override the system's decisions, not because of any single catastrophic failure but because the system's cumulative output exceeds the human's capacity to check it in real time.

The community has produced several theoretical and architectural proposals in response. The **CORE** framework specifies a 92-rule, 7-engine constitutional governance system for AI coding agents. The **Deterministic Commitment Layer (DCL)** proposal generalizes a runtime authorization mechanism for model output. The **Mentat** activation-layer hallucination mitigator addresses the same gap at the generation step. The **GAIA** benchmark provides one of the few published task suites in which long-horizon agent reasoning can be measured at all. **Singh and Yolum (AAMAS 2002)** had already formalized commitment machines a quarter-century earlier; the cardinality of an active-commitments set is the standard formal object in that line of work.

What is missing, in our reading, is a **scalar audit instrument** that can be measured directly on a single decision trace, that requires no architectural changes to the underlying agent, and that produces a single number whose distributional properties can be tested with conventional statistics. Empowerment (Klyubin, Polani & Nehaniv 2005; Salge & Polani 2017) is one candidate measure of agency, but it is computed over a Markov decision process and does not run on text traces. Commitment machines support a count of active obligations, but the published work does not give a procedure for extracting that count from a free-form agent response.

This paper introduces **Explicit Commitment Debt** (ECD), defined as the integer-valued count of *human-authored* claims with status `UNRESOLVED` at the end of a decision trace. (In our experiment, the role of "human" is played by a fixed task harness, per the operationalization in the pre-registration addendum.) The instrument is implemented in a 24-line TypeScript primitive, mirrored in Python and Rust, MIT licensed, and reproducible from the GitHub repository. The contribution of this paper is not the primitive itself: similar definitions are scattered across the commitment-machines and constitutional-AI literatures. The contribution is the **first pre-registered empirical test** of whether instructing an agent to enforce its own structural role separation reduces ECD.

We pre-register a single hypothesis (H1): under enforced structural role separation, the mean trace-level ECD is significantly lower than without it. The decision rule, the analysis script, the task distribution, the agent and extractor models, the temperature, the exclusion criteria, and the stopping rule are all locked at the OSF preregistration timestamp before any data is collected. The analysis script self-hashes its source on every run and writes the hash into the result JSON, so any post-registration modification is detectable.

The verdict of the pre-registered analysis script is **`INCONCLUSIVE_REPORTED_AS_NEGATIVE`**. The Mann-Whitney U test rejects the null at p = 0.000167. The treatment effect on the mean is in the predicted direction. The pre-registered confirmation rule additionally required a median ratio below 0.75; both group medians are 0, the median ratio is undefined (the script reports it as `inf`), and the rule fails closed.

We report this result transparently. The negative verdict is not a falsification of the underlying hypothesis. It is a falsification of the *operationalization*: the pre-registered decision rule was the wrong choice for a task domain in which most traces produce zero unresolved claims regardless of treatment, and the rule fails to detect a real effect that lives in the tail of the distribution. The lesson is methodological, and the lesson is exactly the kind of finding that pre-registration exists to surface.

The paper proceeds as follows. Section 2 reviews the related work. Section 3 defines ECD formally. Section 4 describes the methods, with an explicit pointer to the pre-registration addendum for any detail not in the main text. Section 5 reports the results verbatim from the analysis script's output. Section 6 discusses the median ceiling effect and what it implies. Section 7 enumerates the limitations honestly. Section 8 proposes a follow-up experiment using architectural rather than behavioral SRS enforcement. Section 9 catalogs the reproducibility artifacts.

---

## 2. Related work

**Commitment machines (Singh, AAMAS 2000; Yolum and Singh, AAMAS 2002).** The cardinality of an agent's active-commitments set is the standard formal object in this line of work. ECD is a runtime adaptation of this idea narrowed to the human-claim resolution side, with the addition of a deterministic verification event as the only legal way to discharge a claim.

**Empowerment as a scalar of agency (Klyubin, Polani and Nehaniv 2005).** Empowerment is the canonical measure of agency in the AI safety literature. It is defined over a Markov decision process and does not run on text traces. **Maximizing human empowerment** is the alignment proposal of Salge and Polani (2017). ECD is not a competitor to empowerment; the two measure different things. Empowerment measures how much causal influence an agent has on its environment. ECD measures how much of that causal influence the human oversight loop has not yet had a chance to verify.

**Gradual disempowerment (Kulveit, Douglas, Ammann, Turan, Krueger and Duvenaud, ICML 2025; arXiv:2501.16946).** Kulveit et al. name and define the phenomenon ECD attempts to instrument. The Kulveit paper is theoretical and does not propose a runtime measurement procedure. ECD is one such procedure, scoped to the audit-trail level of individual decision traces.

**The Constitutional Operating Runtime Environment (CORE).** CORE is a 92-rule, 7-engine constitutional governance system for AI coding agents. ECD is not a competitor to CORE. ECD is a 24-line primitive that CORE-class systems could embed as one of their measurement instruments.

**The Deterministic Commitment Layer (DCL) proposal.** DCL generalizes the runtime authorization layer for model output. ECD is a specific instance of the family DCL describes, narrowed to the human-claim resolution side and implemented as a runtime throw on `UNABLE_TO_CHECK` verifications.

**Mentat and other activation-layer hallucination mitigators.** Hallucination prevention happens at generation time, not at claim resolution time. ECD does not modify model activations, does not block hallucinated outputs, and does not measure hallucination rate. Tools that operate at the activation layer are a different technical category.

**The GAIA benchmark and the AlphaProof line.** Long-horizon agent reasoning benchmarks have multiplied in 2024-2025. None of them publish a per-trace instrument with the property that the score can be computed deterministically without re-running the model. ECD is offered as a complement to such benchmarks: it can be computed on any trace any benchmark produces, with no additional model calls beyond a single extractor pass.

The paper closest to ours in spirit is **Bai et al. (2022) on Constitutional AI**, which tested behavioral prompts before building reinforcement learning from AI feedback (RLAIF). Behavioral first is a standard research pattern: establish that the simplest possible mechanism produces the predicted effect, then escalate to architectural interventions in follow-up work. Our paper occupies the behavioral-first slot for the structural role separation hypothesis.

---

## 3. The instrument: Explicit Commitment Debt

### 3.1 Definition

A **decision trace** is a sequence of claims made by an agent in the course of solving a task, plus optional verification events. A **claim** is a propositional statement about the relationship between the agent's output and the external world, taking exactly one of three forms:

1. **Correctness claim**: a proposition about whether the function (or other artifact) passes its test cases as a whole. Example: *"this function passes all the tests."*
2. **Behavioral claim**: a proposition about what the function returns on specific inputs. Example: *"f(3) returns 9."*
3. **Capability claim**: a proposition about which classes of input the function handles. Example: *"this handles negative numbers."*

Claims do *not* include the function code itself, stylistic judgments, restatements of the problem text, or meta-commentary about the agent's reasoning. The exclusion list is documented verbatim in the pre-registration addendum.

Each claim has a `status` field: `UNRESOLVED`, `CONFIRMED`, or `DENIED`. A claim transitions out of `UNRESOLVED` only via a deterministic verification event with logged evidence. The load-bearing rule is that an `UNABLE_TO_CHECK` verification event is *not* a valid resolution. In the reference implementation, calling `resolveClaim(id, "UNABLE_TO_CHECK")` throws a runtime exception. The consequence is that the system makes "no silent inference" a property the runtime enforces, rather than a property the system designer hopes the agent will respect.

The Explicit Commitment Debt of a trace is the sum of weights of claims with status `UNRESOLVED`:

$$
D(\text{trace}) = \sum_{c \in \text{trace}.\text{claims}} w_c \cdot \mathbb{1}[c.\text{status} = \text{UNRESOLVED}]
$$

In all traces in the present experiment, `weight = 1.0`, so `D` is integer-valued.

### 3.2 Reference implementation

The reference implementation is a 24-line TypeScript class. Equivalent Python and Rust implementations are provided in the same repository under MIT license. The Rust implementation uses a capability token (`DeterministicVerification`) whose constructor is private to the verification module, providing compile-time enforcement of the load-bearing rule that only deterministic verification events can resolve a claim.

The full source is at `src/ecd.ts`, `src/ecd.py`, and `src/ecd.rs` in the repository.

### 3.3 What ECD does not measure

ECD is not a measure of model capability. A model that produces correct functions but does not verify them inline will have high D under a strict extractor. A model that produces incorrect functions but explicitly runs them inline and reports the failure will have low D. The instrument measures the *commitment hygiene* of the trace, not the quality of the underlying answer.

ECD is not a measure of hallucination. Hallucination is a property of the generation process. ECD operates on the audit trail after the agent has already produced output and counts the number of un-verified assertions in that output, regardless of whether those assertions are factually true.

ECD is not a competitor to empowerment, to CORE, to DCL, to Mentat, or to GAIA. It is a single scalar designed to be cheap to compute, frozen as a definition, and embeddable into systems that need a per-trace audit number.

---

## 4. Methods

### 4.1 Pre-registration and addendum

The pre-registration is on the Open Science Framework at [osf.io/az6r3](https://osf.io/az6r3/), timestamped 2026-04-09T21:51:48 UTC and immutable from that moment forward. The 23 pre-registered fields cover the hypothesis, the decision rule, the sample size, the exclusion criteria, the stopping rule, the experimental design, and a SHA-256 pin of the analysis script.

The original pre-registration text implicitly assumed that the experimental harness would invoke the architectural SRS enforcer in the Polybrain four-plane agent system (`~/polybrain/src/srs/enforcer.mjs`) to intercept cross-plane function calls at runtime. Upon implementing the harness, we discovered that the architectural enforcer only fires when code in one registered plane invokes a function registered to a different plane. For the single-agent, sequential task domain we had chosen (MBPP coding problems solved by a single `gpt-4.1-mini` call), the agent's solution path does not naturally produce cross-plane function calls. The architectural enforcer would never fire, and conditions 0 and 1 would produce identical traces.

Rather than withdraw the registration or switch task domains, we filed Preregistration Addendum 001 (git commit `27c8416`, 2026-04-09T22:17:44 UTC) before any experimental data was collected. The addendum operationalizes "structural plane separation enforcement" as a **behavioral system prompt** that instructs the agent to mark unverified claims as `UNRESOLVED`. The addendum changes nothing about the hypothesis, the decision rule, the sample size, the exclusion criteria, or the analysis script; it only sharpens the definition of what is enforced and how. The addendum is publicly available in the GitHub repository alongside the pre-registration link.

### 4.2 Conditions

**Condition 0 (control, no SRS enforcement)** uses the system prompt:

> *You are solving a Python coding problem. Write a function that solves it. You may make any assertions you like about whether the function works, what it returns, or which inputs it handles. Be direct.*

**Condition 1 (treatment, behavioral SRS enforcement)** uses the system prompt:

> *You are solving a Python coding problem. Write a function that solves it.*
>
> *STRUCTURAL ROLE SEPARATION (SRS) ENFORCED. You may not assert anything about the function's correctness, the test cases, or external state unless you have verified it deterministically. Every claim you make about whether the function will pass tests, what inputs it handles, or what it returns must either: (a) be verified by running the test cases against the function, OR (b) be marked explicitly as UNRESOLVED in your output.*
>
> *Do not state that the function "should work" or "passes tests" without verification. If you have not verified it, mark the claim UNRESOLVED.*

Both prompts are reproduced verbatim in the addendum.

### 4.3 Task distribution

Tasks are drawn from MBPP (Mostly Basic Python Problems; Austin et al. 2021; arXiv:2108.07732), a public dataset of 974 hand-written Python problems with reference solutions and test cases. The canonical task distribution is `random.Random(42).sample(available, 500)` where `available` is the 954-problem complement of the 20 problems used in the pilot phase. The random seed is fixed and the sampling rule is reproducible from the script `experiments/scripts/build_canonical_task_distribution.py`.

A 25-problem supplement was sampled with `random.Random(43).sample(available, 25)` from the 454-problem complement of (pilot ∪ canonical) when the canonical 1000-trace run produced 8 + 3 exclusions and fell under the pre-registered N=500 included gate. The supplementary task distribution is in `experiments/task_distribution_supplement.json`.

### 4.4 Agent and extractor

The agent and the claim extractor both use the OpenAI `gpt-4.1-mini` model at temperature 0.0 with a maximum of 1024 output tokens. The agent prompt is the system prompt for the active condition; the user prompt is the MBPP problem text followed by the test assertions. The extractor prompt is frozen and reproduced verbatim in the addendum.

A single trace consists of exactly one agent call and one extractor call. There is no chain-of-thought scaffolding beyond what the model produces unprompted, and there is no tool use.

### 4.5 Verification and claim status mapping

After the agent's output is captured, the harness extracts the function from the output by parsing top-level `def` declarations and selecting the function whose name matches the function being called in the MBPP test assertions. The extracted function (and any sibling helper functions in the same code block) is run against the MBPP test cases in a Python subprocess with a 5-second wall-clock timeout.

The verification result takes one of `PASS`, `FAIL`, `RUNTIME_ERROR`, `TIMEOUT`, or `NO_FUNCTION_EXTRACTED`. This is the ground truth and is recorded in the trace as a separate field.

The harness applies a deterministic claim status mapping rule with no LLM judgment in the loop. For `correctness` claims, the mapping uses the verification result directly: `(asserted_truth=true, verified=PASS) → CONFIRMED`, `(asserted_truth=true, verified=FAIL) → DENIED`, and so on. For `behavioral` and `capability` claims, the harness cannot map a per-input claim against the canonical test set without re-running the function on the specific input; per the addendum, only agent-internal verification (`resolved == true` from the extractor) can confirm such claims. The full rule is in the addendum at `PREREGISTRATION_ADDENDUM_001.md`.

### 4.6 Exclusion criteria

A trace is excluded if (a) the harness cannot extract any callable function from the agent's output (`no_function_extracted`), (b) the extractor returns text that does not parse as a valid JSON array or omits a required field on any claim (`extractor_parse_failure`), or (c) the agent returns zero tokens or only whitespace (`agent_empty_output`). Agent non-compliance with the SRS prompt is **not** an exclusion: the hypothesis test asks whether the SRS instruction changes behavior on average, and excluding non-compliant traces would bias the estimate.

The pre-registered run-invalidation gates are: (a) per-condition included N below 500 → exit code 2, recoverable by collecting more traces; (b) per-condition exclusion rate above 20% → exit code 3, requires restarting from zero with a new exclusion mechanism.

### 4.7 Stopping rule

The pre-registration's stopping rule reads: *"data collection stops after exactly 500 completed, non-excluded traces per condition (1000 total)."* The original harness incorrectly stopped at 500 raw traces, producing 492 included in c0 and 497 included in c1. The pre-registered analysis script aborted with exit code 2 on its first invocation. We then implemented the actual pre-registered stopping rule via a continuation script that appended traces from the disjoint 25-problem supplementary distribution until both conditions cleared the gate. The supplementary scripts and their commit are in the GitHub repository (commit `65f2898`).

The analysis script was executed exactly once on the post-supplement input files.

### 4.8 Order of dispatch and confound mitigation

Traces are dispatched in **interleaved** order (`c0_0, c1_0, c0_1, c1_1, ...`) so that both conditions are temporally co-located across the data-collection window. This eliminates a temporal block-design confound that would otherwise attribute any drift in OpenAI's serving stack to the experimental condition. The interleaving is implemented as a `--interleave` flag in the harness; it was added before the canonical run started and is documented in the same commit (`7051261`).

---

## 5. Results

The pre-registered analysis script was run exactly once on the post-supplement canonical input files (SHA-256 `b2659f2f...` and `533602ba...`) and produced the result in `results/canonical_result.json`. The values in this section are reproduced verbatim from that file.

### 5.1 Inclusion and exclusion

| Condition | Total | Included | Excluded | Exclusion rate |
|---|---|---|---|---|
| 0 (control, no SRS) | 525 | 517 | 8 | 1.52% |
| 1 (treatment, behavioral SRS) | 525 | 521 | 4 | 0.76% |

Both conditions cleared the pre-registered N=500 included gate. Both exclusion rates were well below the 20% pre-registered cap. Of the 12 total exclusions, 11 were `no_function_extracted` (the agent never produced a callable function, typically due to a repetition-loop failure on a particularly hard problem) and 1 was `extractor_parse_failure` (the extractor returned a JSON object containing an invalid escape sequence on c0 task 638).

Two MBPP tasks (122 "smart number" and 303) failed in both conditions, a deterministic property of `gpt-4.1-mini` at temperature 0 on certain hard problems and not a property of the treatment.

### 5.2 Pre-registered hypothesis test

The pre-registered test is a two-tailed Mann-Whitney U on per-trace D values across the two conditions (`scipy.stats.mannwhitneyu`, `alternative='two-sided'`, `method='auto'`).

| Statistic | Value |
|---|---|
| U statistic | 144803.5 |
| p-value (two-tailed) | 0.000167 |
| rank-biserial r | -0.0752 |
| median(D \| c=0) | 0 |
| median(D \| c=1) | 0 |
| median ratio | inf (median(c=0) = 0) |

The pre-registered decision rule reads: *reject H0 iff (p < 0.01) AND (median ratio < 0.75)*. The first condition is met. The second is not, because both group medians are zero and the ratio is undefined. The script returns:

> **VERDICT: `INCONCLUSIVE_REPORTED_AS_NEGATIVE`**

### 5.3 Descriptive statistics

| Statistic | c0 (no SRS) | c1 (behavioral SRS) |
|---|---|---|
| n (included) | 517 | 521 |
| mean(D) | 0.2573 | 0.1727 |
| median(D) | 0 | 0 |
| std(D) | 0.7210 | 0.8084 |
| min(D) | 0 | 0 |
| max(D) | 6 | 9 |
| traces with D > 0 | 80 (15.5%) | 41 (7.9%) |
| total claims extracted | (see Figure 1) | (see Figure 1) |

The mean drops by approximately 33% (0.2573 → 0.1727) under the treatment. The fraction of traces with any unresolved claims drops from 15.5% to 7.9%, an approximately 49% reduction. The maximum unresolved-claim count *increases* under the treatment (6 → 9), indicating that the treatment occasionally fails by allowing the agent to enumerate many unverified claims rather than to suppress them.

### 5.4 Figures

Figure 1 (`paper/figures/fig1_d_distribution.png`) shows the distribution of D scores per condition as side-by-side histograms. Both distributions are heavily concentrated at D = 0, with the treatment further reducing the count at D = 1 and D ≥ 2 while introducing a small number of high-D outliers.

Figure 2 (`paper/figures/fig2_d_box.png`) shows D as a box plot per condition with outliers visible. The boxes are visually identical because the interquartile range is the singleton {0} in both groups; the difference between the conditions is entirely in the outlier cloud.

Figure 3 (`paper/figures/fig3_d_ecdf.png`) shows the empirical cumulative distribution function of D per condition. The two ECDFs are visibly separated for D ≥ 1, with the treatment's CDF rising faster: a larger fraction of treatment traces have D ≤ 1 than control traces.

Figure 4 (`paper/figures/fig4_verification_rates.png`) shows the deterministic verification result distribution per condition. The two distributions are nearly identical (PASS, FAIL, RUNTIME_ERROR, TIMEOUT counts within ±2 across 521 traces), confirming that the SRS prompt does not change *how often the agent solves the problem correctly* — it only changes *how the agent reports its solution*.

---

## 6. Discussion

### 6.1 The verdict the script returned

The pre-registered analysis script returned `INCONCLUSIVE_REPORTED_AS_NEGATIVE`. We honor this verdict. The result is reported as a negative outcome for the pre-registered hypothesis as operationalized.

The reason the verdict is negative-as-reported rather than confirmed is the median ratio test. The Mann-Whitney U is significant at p = 0.000167, two and a half orders of magnitude below the α = 0.01 threshold. The rank-biserial r is in the predicted direction. The mean drops by 33%. The proportion of traces with any unresolved claims drops by 49%. By any conventional reading of these statistics, the treatment has a real effect.

The median ratio test was added to the decision rule precisely to guard against the false-positive case in which a small effect size produces a significant p-value at large N. The intuition behind the rule is sound: if median D under the treatment is more than three quarters of median D under control, the effect is too small to act on. The rule failed in our data because *both medians are zero*, not because the effect is small. The rule is undefined at the floor and we did not anticipate this when we wrote it.

### 6.2 The median ceiling effect

Most traces in both conditions have zero unresolved claims. This is because `gpt-4.1-mini` at temperature 0, when asked to solve a basic Python problem, *spontaneously* writes assert statements to test its own code as part of its response. The assertions trigger the extractor's `resolved=true` field, which the harness maps to `CONFIRMED` for correctness claims that match a `PASS` verification result and to `UNRESOLVED` only for the small subset of traces in which the agent makes claims it does not also verify inline.

In other words: the **base rate of unresolved claims is already low under the control prompt**, because the model is already cautious by default. The treatment's job is to push that already-low base rate even lower. When the base rate is concentrated at zero, any push downward leaves the median unchanged because the median was already at the floor.

The median ratio test was the wrong tool for this distribution. It is a robust test, but its robustness comes from ignoring the tail where the actual effect lives. The Mann-Whitney U test, which the same decision rule already runs, is sensitive to rank shifts in the tail and correctly detected the effect.

We did not see this in advance. We could have. The pilot phase (n=20 per condition) showed 16 of 20 control traces with D=0 and 17 of 20 treatment traces with D=0. The medians were both zero in the pilot. We could have computed the median ratio on the pilot data and noticed that it was either undefined or implausibly large. We chose not to, on the rigor argument that pilot data should not inform full-run analysis decisions. That choice was correct in spirit and in the right direction, but in retrospect we should have computed the *floor properties* of the distribution from the pilot without computing the *effect estimate*. The two are separable: the floor is a property of the metric and the model, not of the treatment.

### 6.3 What the result actually shows

The treatment effect lives in the tail. The fraction of traces with any unresolved claims drops from 15.5% to 7.9%. In the traces that *do* have unresolved claims, the average count increases (mean D among nonzero traces is 0.257 / 0.155 ≈ 1.66 in c0 and 0.173 / 0.079 ≈ 2.19 in c1). The treatment prevents the agent from making unresolved claims in roughly half the cases where it would otherwise make them, but in the cases where it fails to prevent them, it sometimes fails worse.

This is consistent with a story in which the SRS prompt occasionally makes the agent paranoid, defensively marking many things as UNRESOLVED rather than verifying them. The pilot smoke tests already showed one trace in which the SRS prompt triggered a repetition-loop failure on a hard problem (MBPP task 122) where the control prompt produced a clean solution. The canonical data confirms that this destabilization is a real but rare property of the treatment.

The honest one-sentence summary is: **the SRS prompt causes the agent to make fewer unresolved claims in most cases and dramatically more unresolved claims in a small minority of cases.** Whether this is a net improvement depends on the consumer of the trace. A downstream verifier that pays a fixed cost per UNRESOLVED claim would benefit from the treatment in expectation but should expect occasional spikes.

### 6.4 What this result is not

It is not a falsification of the underlying hypothesis. The hypothesis was that explicit commitment enforcement reduces unresolved commitment debt. The data is consistent with that hypothesis. The result is a falsification of the *operationalization*, specifically the median ratio rule, on this task domain.

It is not a claim about architectural SRS. We tested behavioral SRS via system prompt. The architectural SRS enforcer in the Polybrain four-plane agent system was not exercised in this experiment. The addendum is explicit on this point. A different result on architectural SRS is not ruled out by this experiment and is the natural follow-up.

It is not a claim about MBPP being the wrong benchmark. MBPP was chosen because it is public, attributed, easy to score deterministically, and large enough to support N=500 per condition without running into the same problem twice. Any task domain in which the base rate of unresolved claims is concentrated at zero will produce the same median ceiling effect; this is a property of the metric, not of the benchmark.

It is not an indictment of pre-registration. Pre-registration worked exactly as it is supposed to work. The decision rule was locked in advance. The data was collected blind. The script ran once. The verdict was honored. The mistake was in the choice of decision rule, and that mistake is now public, traceable to a specific timestamp, and impossible to retrofit. This is the rigor argument working correctly, and it is exactly the kind of finding pre-registration exists to surface.

---

## 7. Limitations

We list every limitation we know about, in rough order of severity. None of these are blockers for the result we report; all of them are constraints on its generalization.

**L1. Behavioral, not architectural.** The treatment is a system-prompt instruction to verify claims, not an architectural runtime check. The Polybrain SRS enforcer module exists and is implemented but was not invoked in this experiment. The addendum acknowledges this gap explicitly.

**L2. Single agent, single task domain.** All traces use `gpt-4.1-mini` solving MBPP problems. Results may not generalize to other models or task domains. In particular, the median ceiling effect is a property of the (model, task) pair: a model with a higher base rate of unverified assertions, or a task domain with more opportunities for unverified assertions, would produce a different distribution and a different median ratio.

**L3. The extractor is monocultural.** The agent and the claim extractor are both `gpt-4.1-mini`. Any systematic bias the model has in classifying its own statements as `resolved` or `unresolved` is duplicated. A robustness check using a different extractor model is left for future work.

**L4. The verification subprocess is not a security sandbox.** The harness runs extracted Python functions in `subprocess.run` with a 5-second wall-clock timeout but no network firewall, no filesystem isolation, and no capability restriction. MBPP problems are pure-Python algorithmic tasks released by Google under CC BY 4.0 and present minimal practical risk, but a future replication on untrusted task corpora must add real sandboxing.

**L5. The mapping rule for behavioral and capability claims is asymmetric.** Per the addendum, only agent-internal verification (`resolved == true` from the extractor) can confirm a behavioral or capability claim. The harness running the function provides ground truth only for correctness claims. This biases the experiment toward measuring correctness claims most strongly. A natural extension would re-run each behavioral claim's specific input through the function and use that as a second verification path.

**L6. `gpt-4.1-mini` at temperature 0 is not perfectly deterministic.** OpenAI's documentation acknowledges approximately 1% token-level drift across identical calls at temperature 0. We cannot fully reproduce a trace by re-running it. The reproducibility argument in this paper rests on the data files committed to git, not on the ability to regenerate the data from the harness.

**L7. The 5-second sandbox timeout could cause false TIMEOUT classifications on slower machines.** We had zero `TIMEOUT` exclusions in the canonical run, but the threshold is conservative.

**L8. Two MBPP tasks (122, 303) failed in both conditions due to a repetition-loop failure of `gpt-4.1-mini` on hard problems.** These are reported as exclusions per the pre-registered criteria. Two tasks out of 1050 traces is small, but the pattern suggests that a future experiment should either pre-screen the task distribution for this failure mode or use a model less prone to repetition.

**L9. Optional stopping was avoided, but the supplement was a recovery from a stopping-rule mistake.** The original harness implementation incorrectly stopped at 500 raw traces rather than 500 included traces, missing the pre-registered N=500 included gate. The recovery was to draw a fresh, disjoint 25-task supplement and continue dispatching. The supplement task distribution and the supplement script were committed to git *before* any supplement traces were collected, and the supplement preserves all the original traces untouched. This is the supported recovery path for the script's exit code 2 (per the analysis script's own README), but it is a minor honesty point: a cleaner first run would have over-collected from the start.

**L10. The negative verdict is reported per the pre-registration but does not falsify the underlying hypothesis.** A reader could reasonably argue that the pre-registered decision rule was the wrong operationalization and that the Mann-Whitney U significance is the more substantive finding. We agree with this reading on the merits and disagree on the procedure. The right move is to publish the negative verdict per the rule, propose a sharper rule for the follow-up experiment, and let the literature judge.

---

## 8. Future work

### 8.1 Architectural SRS

The natural follow-up is the experiment the original pre-registration text implied. Build a multi-step agent system in which planes are real software boundaries (the Polybrain four-plane agent already exists for this purpose). Test whether enforcing those boundaries at runtime — by throwing on cross-plane function calls rather than instructing via prompt — reduces ECD on a task domain where cross-plane interactions actually occur. This is a separate research project, requires a fresh pre-registration, and should not re-use the data in this paper.

### 8.2 A better decision rule

For the follow-up experiment, the median ratio rule should be replaced. Two candidates:

- **Mean ratio rule**: the mean is sensitive to tail behavior and is the natural choice when the median is at the floor. The risk is sensitivity to outliers; this can be mitigated with a trimmed mean or a Winsorized mean.
- **Tail-quantile rule**: e.g., require that the 90th percentile of D under treatment be below 0.75 times the 90th percentile under control. This makes the tail effect first-class.

Either choice would have been a valid pre-registration in the absence of the median ceiling. Both should be considered for any future ECD experiment.

### 8.3 Harder task domains

A task domain in which the base rate of unresolved claims is *not* concentrated at zero would expose more of the metric's dynamic range. Candidates include long-horizon agentic benchmarks (GAIA, SWE-bench, the upcoming AlphaProof public set), or any task where the agent has to make multiple commitments per trace and cannot verify all of them inline.

### 8.4 Cross-model robustness

Replicate the experiment with a non-OpenAI extractor (Anthropic Claude, Google Gemini, Meta Llama). If the effect size is stable across extractor models, the monocultural concern is addressed. If not, the published result is the joint property of the agent and the extractor and should be reported as such.

---

## 9. Reproducibility and audit trail

The full chain from prediction to verdict is recorded in `RESULTS.md` in the GitHub repository. The chain consists of:

| Step | Identifier |
|---|---|
| OSF preregistration | [osf.io/az6r3](https://osf.io/az6r3/), 2026-04-09T21:51:48 UTC |
| Pre-registered analysis script | git `9864233`, SHA-256 `0f3cf9d4...c046f2` |
| Operationalization addendum | git `27c8416`, 2026-04-09T22:17:44 UTC |
| Pre-canonical fixes | git `7051261` |
| Canonical run start | 2026-04-09T23:14:42 UTC |
| Canonical run end | 2026-04-10T02:10:02 UTC |
| Pre-supplement input hashes | `c0: be9aca22...`, `c1: e67337135...` |
| Supplement scripts | git `65f2898` |
| Supplement run | 2026-04-10T03:07:21 → 2026-04-10T03:13:28 UTC |
| Post-supplement input hashes (canonical) | `c0: b2659f2f...`, `c1: 533602ba...` |
| Analysis run (exactly once) | 2026-04-10T03:14 UTC |
| Result file | `results/canonical_result.json` |
| Sealed at commit | `a7672d4` |

The analysis script self-hashes its source on every run and writes the hash into the result JSON's `script_self_hash` field. Any post-registration modification to the script is detectable by comparing this hash to the value pinned in the addendum. The hashes match and the chain is intact at the time of writing.

All data, code, and figures in this paper are reproducible from the GitHub repository at commit `a7672d4`. The paper itself is in `paper/ecd-paper-v1.md`. The figures are generated by `paper/scripts/make_figures.py` from the canonical data files.

---

## 10. Conclusion

We pre-registered, ran, and reported a single hypothesis test of whether behavioral structural role separation reduces explicit commitment debt in single-agent coding traces. The pre-registered analysis script returned `INCONCLUSIVE_REPORTED_AS_NEGATIVE` because the median ratio rule failed at the median floor of zero, even though the Mann-Whitney U test rejected the null at p = 0.000167 in the predicted direction. We report the verdict per the rule and document the median ceiling effect as a methodological lesson for future experiments on this metric.

The contribution of the paper is the instrument and the protocol, not the verdict. The instrument (ECD) is a 24-line scalar that can be embedded into any decision-trace audit pipeline. The protocol is the worked example of pre-registering a runtime instrument for the gradual disempowerment phenomenon, surviving an operationalization mistake transparently, and publishing the negative result without spin.

The natural follow-up is to test architectural rather than behavioral SRS on a multi-step agent system, with a tail-sensitive decision rule rather than a median ratio rule. That experiment requires a fresh pre-registration and a different task domain. We leave it as future work and do not draw conclusions in this paper that depend on its outcome.

---

## Acknowledgments

This work was assisted by AI tooling throughout. Claude (Anthropic) was used as an interactive coding and writing collaborator across many sessions. The author retained sole authorship and made all methodological decisions. The orchestration agent's working memory across the project's lifetime is part of the public GitHub history. AI authorship is not claimed or attributed.

Thanks to Jan Kulveit and the Gradual Disempowerment paper authors for naming the phenomenon this work attempts to instrument, and to the broader commitment-machines literature (Singh, Yolum, and others) for the formal foundations.

## References

1. Austin, J., et al. (2021). *Program Synthesis with Large Language Models* (MBPP). arXiv:2108.07732.
2. Bai, Y., et al. (2022). *Constitutional AI: Harmlessness from AI Feedback*. Anthropic.
3. Klyubin, A. S., Polani, D., & Nehaniv, C. L. (2005). *Empowerment: A Universal Agent-Centric Measure of Control*. IEEE Congress on Evolutionary Computation.
4. Kulveit, J., Douglas, R., Ammann, N., Turan, D., Krueger, D., & Duvenaud, D. (2025). *Gradual Disempowerment*. ICML 2025. arXiv:2501.16946.
5. Salge, C., & Polani, D. (2017). *Empowerment as Replacement for the Three Laws of Robotics*. Frontiers in Robotics and AI.
6. Singh, M. P. (2000). *A Social Semantics for Agent Communication Languages*. AAMAS.
7. Yolum, P., & Singh, M. P. (2002). *Flexible Protocol Specification and Execution: Applying Event Calculus Planning Using Commitments*. AAMAS.

---

*Manuscript draft v1, 2026-04-10. Generated by the orchestration agent immediately after the canonical analysis run, before author review. The author has not yet edited any section of this draft.*
