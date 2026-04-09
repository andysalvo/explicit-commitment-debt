# Experiments

This directory contains the experimental harness referenced in the OSF preregistration.

## Critical rigor rule

**Do NOT run `srs_ecd_experiment.py` at full scale until the OSF preregistration has been timestamped.** The whole point of preregistration is that the experimental data does not exist when the prediction is locked. Running the experiment before Register is clicked invalidates the rigor of the entire enterprise.

**You may** read the source, fill in the scaffold, and run the smoke test. **You may not** generate canonical data files until the OSF Register button has been clicked and the registration ID is recorded in `data/SCHEMA.md`'s history.

## Files

- `srs_ecd_experiment.py` — the experimental harness scaffold. Currently raises `NotImplementedError` in `run_single_trace()` so it cannot accidentally produce real-looking data. Wire it to a real multi-LLM agent dispatch to enable.
- `task_distribution.json` — the fixed task set used in both conditions. Same tasks for SRS-enforced and no-SRS runs. NOT YET WRITTEN.
- (after both runs) `../data/condition_0.jsonl` — primary dataset for no-SRS condition (500+ traces)
- (after both runs) `../data/condition_1.jsonl` — primary dataset for SRS-enforced condition (500+ traces)

## How to run (after preregistration is locked)

```bash
# Condition 0 (no SRS enforcement)
python experiments/srs_ecd_experiment.py \
    --condition 0 \
    --n-traces 500 \
    --output data/condition_0.jsonl \
    --task-distribution experiments/task_distribution.json \
    --seed 42 \
    --allow-scaffold

# Condition 1 (SRS enforcement)
python experiments/srs_ecd_experiment.py \
    --condition 1 \
    --n-traces 500 \
    --output data/condition_1.jsonl \
    --task-distribution experiments/task_distribution.json \
    --seed 42 \
    --allow-scaffold

# Run the canonical analysis exactly once
python tests/preregistered_analysis.py \
    --condition-0 data/condition_0.jsonl \
    --condition-1 data/condition_1.jsonl \
    --output      results/canonical_result.json
```

## Pre-registered exit codes

The analysis script uses these exit codes deterministically:

| Exit | Meaning |
|---|---|
| `0` | Hypothesis CONFIRMED (p < 0.01 AND median ratio < 0.75) |
| `1` | Hypothesis FALSIFIED or INCONCLUSIVE (negative result publishable) |
| `2` | Either condition has fewer than 500 included traces — run is invalid |
| `3` | Either condition has exclusion rate > 20% — run is invalidated, restart from zero |

## Reproducibility checklist (before declaring the run canonical)

- [ ] OSF preregistration timestamp captured (registration ID in this README)
- [ ] `tests/preregistered_analysis.py` git commit hash captured (in OSF preregistration)
- [ ] `experiments/srs_ecd_experiment.py` git commit hash captured
- [ ] `experiments/task_distribution.json` git commit hash captured
- [ ] Fixed seed `--seed 42` used in both conditions
- [ ] Both conditions run with identical model configuration (model name, temperature, max tokens)
- [ ] Both conditions run on the same hardware
- [ ] `data/condition_0.jsonl` and `data/condition_1.jsonl` SHA-256 hashes captured before analysis
- [ ] `tests/test_analysis_smoke.py` passes against the analysis script
- [ ] Analysis script run exactly ONCE on the full dataset

## What goes in `task_distribution.json`

A JSON array of task objects:

```json
[
  {
    "task_id": "task-001",
    "task_text": "Write a Python function that reads a CSV file and returns the column names.",
    "expected_human_claims": 3
  },
  ...
]
```

The task distribution is the same across both conditions. The task content is held fixed; only the SRS enforcer flag changes. Task selection within each run is randomized via the fixed seed.
