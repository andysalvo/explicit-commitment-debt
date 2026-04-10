# Canonical Run Results

This document records the canonical outcome of the Explicit Commitment Debt (ECD) experiment preregistered at OSF [`az6r3`](https://osf.io/az6r3/). It is the audit trail that links the preregistration timestamp, the addendum, the analysis script, the input data files, and the verdict. Every artifact referenced here is content-addressed and verifiable.

The verdict is reproduced verbatim from `results/canonical_result.json`. No interpretation, no spin, no narrative is added in this file. The discussion of the result lives in the paper, not here.

## The chain

| # | Artifact | Identifier | Timestamp (UTC) |
|---|---|---|---|
| 1 | OSF preregistration | [`az6r3`](https://osf.io/az6r3/) | 2026-04-09T21:51:48 |
| 2 | Pre-registered analysis script | git commit `986423316badce6a670c84acb35f663a0353602d`, SHA-256 `0f3cf9d4512be12d618a7bf01ba0c5f7f7d2c79e919d03a05583429024c046f2` | 2026-04-09T22:17:44 (commit time of the addendum that pinned the script) |
| 3 | Preregistration Addendum 001 | git commit `27c84165f0a5e6088353e0a10f2c8ac69f0e7094` | 2026-04-09T22:17:44 |
| 4 | Pre-canonical fixes (interleaving, retry, function extraction, sandbox honesty) | git commit `705126195601167aa721a78a2445c2fe3ea19acd` | 2026-04-09 (filed before canonical run started) |
| 5 | Canonical run (1000 traces, blocks of 500/condition) | trace_id prefix `canonical-`, script `experiments/run_pilot.py --interleave` against `experiments/task_distribution_canonical.json` | start 2026-04-09T23:14:42 → end 2026-04-10T02:10:02 (wall clock 2h 55m 20s) |
| 6 | Pre-supplement input hashes (failed analysis at exit code 2) | `condition_0.jsonl` SHA-256 `be9aca2240adf1af5f24c3c5136e75a5c762a01be82108aac253f2e85dc7301d`<br>`condition_1.jsonl` SHA-256 `e67337135d04f3be0f89939c27568bcd278ba5a2c2421d8f13974123d5725961` | 2026-04-10T02:10 (immediately after canonical run) |
| 7 | Supplement scripts (top-up to clear N=500 included gate) | git commit `65f28989d2c54a5b9cd3b1ab51753dad6bda56c6` | filed before supplement run started |
| 8 | Supplement run (50 traces total, 25 per condition, drawn from disjoint MBPP pool with `Random(43)`) | trace_id prefix `canonical-`, trace_idx 500-524, script `experiments/run_canonical_supplement.py` | start 2026-04-10T03:07:21 → end 2026-04-10T03:13:28 (wall clock 6m 7s) |
| 9 | Post-supplement input hashes (canonical input to the analysis script) | `condition_0.jsonl` SHA-256 `b2659f2f743c99c23f0e0cd340b22addb8ea1daaa96820353283c4ac3ddee5c3`<br>`condition_1.jsonl` SHA-256 `533602ba1319e87a335ccf18ffabde71f79e2335a255c0f4ab4e5be65f857f23` | 2026-04-10T03:13 |
| 10 | Canonical analysis output | `results/canonical_result.json` (this commit) | 2026-04-10T03:14 (analysis script ran exactly once) |

The analysis script ran once on artifact #9 and produced artifact #10. It was not run before, it has not been run since, and it will not be run again on this dataset.

## Inclusion and exclusion summary

| Condition | Total | Included | Excluded | Exclusion rate | Gate (≥500 included, ≤20% excluded) |
|---|---|---|---|---|---|
| 0 (control, no SRS prompt) | 525 | 517 | 8 | 1.52% | ✅ |
| 1 (treatment, behavioral SRS prompt) | 525 | 521 | 4 | 0.76% | ✅ |

Both gates pass.

## Exclusion reasons

| Reason | c0 | c1 |
|---|---|---|
| `no_function_extracted` (agent never produced a callable function — typically a repetition-loop failure on a hard MBPP problem) | 7 | 4 |
| `extractor_parse_failure` (extractor LLM returned JSON with an invalid escape character on c0 task 638) | 1 | 0 |

Tasks that produced exclusions: 122, 136, 214, 303, 430, 511, 638, 771 (c0); 122, 303, 493, 609 (c1). Two tasks (122 "smart number," 303) failed in both conditions and are reported in the paper as a deterministic failure mode of `gpt-4.1-mini` at temperature 0 on certain hard MBPP problems. The `493` exclusion is in the supplement batch (trace_idx 502).

## Verdict (verbatim from `results/canonical_result.json`)

```
Mann-Whitney U statistic:        144803.5
p-value (two-tailed):            0.000167123
rank-biserial r:                 -0.0752
median(D | c=0):                 0
median(D | c=1):                 0
median ratio:                    inf  (because median(c=0) is 0)
p < 0.01:                        True
median_ratio < 0.75:             False

VERDICT: INCONCLUSIVE_REPORTED_AS_NEGATIVE
```

Per the preregistered decision rule, the hypothesis is confirmed if and only if the p-value is below `0.01` AND the median ratio is below `0.75`. The first condition is met. The second condition is not (the median is 0 in both groups, making the ratio undefined and the test fail closed). The verdict the script returned is `INCONCLUSIVE_REPORTED_AS_NEGATIVE`.

## Descriptive statistics (verbatim from `results/canonical_result.json`)

| | c0 (no SRS) | c1 (behavioral SRS) |
|---|---|---|
| n (included) | 517 | 521 |
| mean(D) | 0.2572533849129594 | 0.1727447216890595 |
| median(D) | 0 | 0 |
| stdev(D) | 0.7210368901227889 | 0.8083691017713548 |
| min(D) | 0 | 0 |
| max(D) | 6.0 | 9.0 |
| p25(D) | 0 | 0 |
| p75(D) | 0 | 0 |

## What this file does NOT contain

- Any interpretation of the verdict beyond reporting the literal output of the analysis script.
- Any post-hoc statistical test that was not in the preregistration.
- Any rationale for re-running the analysis on this dataset (it will not be re-run).
- Any narrative framing of the result as positive, negative, surprising, or expected. The narrative belongs in the paper.

## What happens next

1. The paper is drafted as a negative-result report. The Mann-Whitney U significance and the median-ceiling effect are both disclosed transparently. The decision rule was preregistered; the rule produced the verdict; the verdict is the contribution.
2. A follow-up experiment may test architectural SRS enforcement (rather than behavioral) on a multi-step agentic task domain where cross-plane function calls actually occur. That experiment, if pursued, will be a separate preregistration on a separate OSF node and will not re-use the data in this file.
3. No re-analysis of `data/condition_0.jsonl` or `data/condition_1.jsonl` is permitted under any circumstance. The files are sealed by the hashes recorded in this document and by the `script_self_hash` field in `results/canonical_result.json`. Any future use of the data must cite this document and the OSF preregistration.

---

*Sealed 2026-04-10. Do not modify the input data files (`data/condition_0.jsonl`, `data/condition_1.jsonl`), the analysis script (`tests/preregistered_analysis.py`), or the result file (`results/canonical_result.json`) after this commit. The hashes above are the audit trail. Any divergence is detectable.*
