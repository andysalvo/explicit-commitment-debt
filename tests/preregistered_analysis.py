#!/usr/bin/env python3
"""
PRE-REGISTERED ANALYSIS SCRIPT — DO NOT MODIFY AFTER DATA COLLECTION BEGINS

This script implements the canonical, immutable analysis specified in the OSF
preregistration for Explicit Commitment Debt (ECD). It is committed to the
public GitHub repository BEFORE any controlled experimental data is collected.

Pre-registered hypothesis (H1):
    In multi-LLM agent decision traces, mean ECD is significantly lower under
    enforced structural plane separation than without it.

Pre-registered decision rule:
    Reject H0 if AND ONLY IF both conditions hold:
      (1) p-value of two-tailed Mann-Whitney U test < 0.01
      (2) median ratio (median D under condition 1 / median D under condition 0) < 0.75

If both conditions hold, the hypothesis is CONFIRMED.
If either condition fails, the hypothesis is FALSIFIED. Negative results are
published per ROADMAP.md sunset criteria.

Inputs:
    --condition-0 PATH    Path to JSONL file of traces under no-SRS condition.
    --condition-1 PATH    Path to JSONL file of traces under SRS-enforced condition.
    --output     PATH     Path to write the canonical results JSON.

Both input files must conform to data/SCHEMA.md.

Usage:
    python tests/preregistered_analysis.py \\
        --condition-0 data/condition_0.jsonl \\
        --condition-1 data/condition_1.jsonl \\
        --output      results/canonical_result.json

Mandatory rigor properties:
    - Computes D per trace by summing weights of claims with status == 'UNRESOLVED'.
    - Excludes any trace with `excluded == true`.
    - If post-exclusion N < 500 in either condition, REFUSES to run and exits 2.
    - If exclusion rate > 20% in either condition, REFUSES to run and exits 3.
    - Uses scipy.stats.mannwhitneyu, alternative='two-sided', method='auto'.
    - Reports p, U, rank-biserial r, median ratio, descriptive stats.
    - Applies the pre-registered decision rule deterministically.
    - Writes a self-hash to the output so any modification is detectable.

License: MIT (same as the rest of the repository).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

# Import scipy at the top so missing-dependency failures happen before any I/O.
try:
    from scipy.stats import mannwhitneyu
except ImportError:
    print(
        "ERROR: scipy is required. Install with `pip install scipy`.",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Pre-registered constants. CHANGING THESE INVALIDATES THE PRE-REGISTRATION.
# ---------------------------------------------------------------------------
ALPHA = 0.01
MEDIAN_RATIO_THRESHOLD = 0.75
MIN_TRACES_PER_CONDITION = 500
MAX_EXCLUSION_RATE = 0.20
SCHEMA_VERSION = "1"


def self_hash() -> str:
    """SHA-256 of this very file. Lets the result JSON identify exactly which
    version of the script produced it. Any modification of the script changes
    this hash and is therefore detectable."""
    p = Path(__file__).resolve()
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_traces(path: Path) -> list[dict]:
    """Load JSONL traces, validate schema_version, return list of dicts."""
    if not path.exists():
        print(f"ERROR: trace file not found: {path}", file=sys.stderr)
        sys.exit(1)
    traces = []
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                trace = json.loads(line)
            except json.JSONDecodeError as e:
                print(
                    f"ERROR: malformed JSON at {path}:{line_num}: {e}",
                    file=sys.stderr,
                )
                sys.exit(1)
            if trace.get("schema_version") != SCHEMA_VERSION:
                print(
                    f"ERROR: trace {trace.get('trace_id', '?')} has "
                    f"schema_version={trace.get('schema_version')!r}, "
                    f"expected {SCHEMA_VERSION!r}",
                    file=sys.stderr,
                )
                sys.exit(1)
            traces.append(trace)
    return traces


def compute_D(trace: dict) -> float:
    """D = sum of weights of claims with status == 'UNRESOLVED'.

    This is the load-bearing measurement function. It must be deterministic
    and must not modify the trace.
    """
    return sum(
        c.get("weight", 1.0)
        for c in trace.get("claims", [])
        if c.get("status") == "UNRESOLVED"
    )


def filter_and_count(traces: list[dict]) -> tuple[list[dict], int, int]:
    """Return (included, excluded_count, total_count)."""
    included = [t for t in traces if not t.get("excluded", False)]
    return included, len(traces) - len(included), len(traces)


def rank_biserial(u_stat: float, n0: int, n1: int) -> float:
    """Rank-biserial correlation as effect size for Mann-Whitney U.
    Defined as: r = 1 - 2U / (n0 * n1). Range [-1, 1].
    """
    return 1.0 - (2.0 * u_stat) / (n0 * n1)


def descriptive(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    sorted_v = sorted(values)
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "stdev": statistics.pstdev(values),
        "p25": sorted_v[len(sorted_v) // 4],
        "p75": sorted_v[(3 * len(sorted_v)) // 4],
        "min": min(values),
        "max": max(values),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Pre-registered Mann-Whitney U analysis for ECD.",
    )
    ap.add_argument("--condition-0", required=True, type=Path)
    ap.add_argument("--condition-1", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    print("=" * 78)
    print("PRE-REGISTERED ANALYSIS — Explicit Commitment Debt")
    print("=" * 78)
    print(f"  script_self_hash: {self_hash()}")
    print(f"  alpha:            {ALPHA}")
    print(f"  median_ratio_max: {MEDIAN_RATIO_THRESHOLD}")
    print(f"  min_n:            {MIN_TRACES_PER_CONDITION}")
    print(f"  max_excl_rate:    {MAX_EXCLUSION_RATE}")
    print()

    # ----- load -----
    traces_0_all = load_traces(args.condition_0)
    traces_1_all = load_traces(args.condition_1)

    traces_0, excl_0, total_0 = filter_and_count(traces_0_all)
    traces_1, excl_1, total_1 = filter_and_count(traces_1_all)

    print(f"  condition_0: {len(traces_0)} included / {excl_0} excluded / {total_0} total")
    print(f"  condition_1: {len(traces_1)} included / {excl_1} excluded / {total_1} total")
    print()

    # ----- enforce pre-registered gates BEFORE any analysis happens -----
    # Exclusion-rate gate runs FIRST: a high exclusion rate invalidates the run
    # regardless of how many included traces remain.
    excl_rate_0 = excl_0 / total_0 if total_0 else 0
    excl_rate_1 = excl_1 / total_1 if total_1 else 0
    if excl_rate_0 > MAX_EXCLUSION_RATE:
        print(
            f"ABORT: condition_0 exclusion rate {excl_rate_0:.2%} > "
            f"{MAX_EXCLUSION_RATE:.0%}. Run is invalid; restart from zero.",
            file=sys.stderr,
        )
        return 3
    if excl_rate_1 > MAX_EXCLUSION_RATE:
        print(
            f"ABORT: condition_1 exclusion rate {excl_rate_1:.2%} > "
            f"{MAX_EXCLUSION_RATE:.0%}. Run is invalid; restart from zero.",
            file=sys.stderr,
        )
        return 3

    if len(traces_0) < MIN_TRACES_PER_CONDITION:
        print(
            f"ABORT: condition_0 has {len(traces_0)} included traces, "
            f"requires >= {MIN_TRACES_PER_CONDITION}. Run is invalid.",
            file=sys.stderr,
        )
        return 2
    if len(traces_1) < MIN_TRACES_PER_CONDITION:
        print(
            f"ABORT: condition_1 has {len(traces_1)} included traces, "
            f"requires >= {MIN_TRACES_PER_CONDITION}. Run is invalid.",
            file=sys.stderr,
        )
        return 2

    # ----- compute D per trace -----
    D_0 = [compute_D(t) for t in traces_0]
    D_1 = [compute_D(t) for t in traces_1]

    # ----- run the pre-registered statistical test ONCE -----
    u_stat, p_value = mannwhitneyu(D_0, D_1, alternative="two-sided", method="auto")
    r = rank_biserial(u_stat, len(D_0), len(D_1))

    median_0 = statistics.median(D_0)
    median_1 = statistics.median(D_1)
    median_ratio = (median_1 / median_0) if median_0 > 0 else float("inf")

    # ----- apply the pre-registered decision rule -----
    p_significant = p_value < ALPHA
    effect_large_enough = median_ratio < MEDIAN_RATIO_THRESHOLD
    hypothesis_confirmed = p_significant and effect_large_enough

    if hypothesis_confirmed:
        verdict = "CONFIRMED"
    elif p_value >= 0.05 or 0.8 <= median_ratio <= 1.25:
        verdict = "FALSIFIED"
    else:
        # Mixed: significant but effect too small, or marginally non-significant.
        verdict = "INCONCLUSIVE_REPORTED_AS_NEGATIVE"

    # ----- print canonical result -----
    print("RESULT")
    print("-" * 78)
    print(f"  U statistic:        {u_stat}")
    print(f"  p-value (2-tailed): {p_value:.6g}")
    print(f"  rank-biserial r:    {r:+.4f}")
    print(f"  median(D | c=0):    {median_0}")
    print(f"  median(D | c=1):    {median_1}")
    print(f"  median ratio:       {median_ratio:.4f}")
    print(f"  p < {ALPHA}:           {p_significant}")
    print(f"  median_ratio < {MEDIAN_RATIO_THRESHOLD}: {effect_large_enough}")
    print()
    print(f"  VERDICT: {verdict}")
    print()
    print("DESCRIPTIVE")
    print("-" * 78)
    print(f"  condition_0: {descriptive(D_0)}")
    print(f"  condition_1: {descriptive(D_1)}")

    # ----- write canonical result JSON -----
    result = {
        "script_self_hash": self_hash(),
        "schema_version": SCHEMA_VERSION,
        "alpha": ALPHA,
        "median_ratio_threshold": MEDIAN_RATIO_THRESHOLD,
        "min_traces_per_condition": MIN_TRACES_PER_CONDITION,
        "max_exclusion_rate": MAX_EXCLUSION_RATE,
        "condition_0": {
            "n_total": total_0,
            "n_included": len(traces_0),
            "n_excluded": excl_0,
            "exclusion_rate": excl_rate_0,
            "descriptive": descriptive(D_0),
        },
        "condition_1": {
            "n_total": total_1,
            "n_included": len(traces_1),
            "n_excluded": excl_1,
            "exclusion_rate": excl_rate_1,
            "descriptive": descriptive(D_1),
        },
        "test": {
            "name": "two-tailed Mann-Whitney U",
            "u_statistic": float(u_stat),
            "p_value": float(p_value),
            "rank_biserial_r": float(r),
            "median_ratio": float(median_ratio),
        },
        "decision": {
            "p_significant_at_alpha": bool(p_significant),
            "median_ratio_below_threshold": bool(effect_large_enough),
            "hypothesis_confirmed": bool(hypothesis_confirmed),
            "verdict": verdict,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True))
    print()
    print(f"  canonical result JSON written to: {args.output}")
    print()

    return 0 if verdict == "CONFIRMED" else 1


if __name__ == "__main__":
    sys.exit(main())
