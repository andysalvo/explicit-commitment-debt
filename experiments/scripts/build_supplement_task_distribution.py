#!/usr/bin/env python3
"""
Build experiments/task_distribution_supplement.json — additional MBPP tasks
used to top up the canonical run after exit code 2 from the analysis script.

Filed in response to: canonical run produced 492 included / 8 excluded in
condition 0 and 497 included / 3 excluded in condition 1, falling under the
preregistered N=500 included gate. The preregistered stopping rule (OSF field
344-55) calls for collecting until 500 INCLUDED traces per condition; the
original harness incorrectly stopped at 500 RAW. The supplement implements the
actual preregistered stopping rule.

Sampling rule (frozen):
    pilot_indices     = first 20 mbpp_index values from task_distribution.json
    canonical_indices = all 500 mbpp_index values from task_distribution_canonical.json
    excluded          = pilot_indices ∪ canonical_indices  (520 total)
    available         = [i for i in range(974) if i not in excluded]   (454 problems)
    supplement        = random.Random(43).sample(available, 25)

This guarantees:
  - The supplement uses 25 MBPP problems disjoint from BOTH the pilot and the canonical run.
  - The seed (43) is different from the pilot/canonical seed (42), so the sample
    is not influenced by knowledge of which canonical tasks failed.
  - The pool is the literal complement of pilot+canonical; no information about
    which specific tasks failed is used in selection.
  - Re-running this script always produces the same file.

Run ONCE. The output is committed before any supplement traces are collected.

Usage:
    python experiments/scripts/build_supplement_task_distribution.py
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RAW = REPO / "experiments" / "data" / "mbpp_raw.jsonl"
PILOT_DIST = REPO / "experiments" / "task_distribution.json"
CANON_DIST = REPO / "experiments" / "task_distribution_canonical.json"
OUT = REPO / "experiments" / "task_distribution_supplement.json"
N = 25
SEED = 43


def main() -> int:
    if not RAW.exists():
        print(f"ERROR: raw MBPP not found at {RAW}", file=sys.stderr)
        return 1
    if not PILOT_DIST.exists() or not CANON_DIST.exists():
        print(f"ERROR: pilot or canonical distribution missing", file=sys.stderr)
        return 1

    raw = [json.loads(line) for line in RAW.read_text().splitlines() if line.strip()]
    if len(raw) != 974:
        print(f"ERROR: expected 974 MBPP problems, found {len(raw)}", file=sys.stderr)
        return 2

    pilot = json.loads(PILOT_DIST.read_text())
    canon = json.loads(CANON_DIST.read_text())
    pilot_indices = sorted({t["mbpp_index"] for t in pilot["tasks"][:20]})
    canon_indices = sorted({t["mbpp_index"] for t in canon["tasks"]})
    excluded = sorted(set(pilot_indices) | set(canon_indices))
    print(f"pilot_indices ({len(pilot_indices)}): {pilot_indices}")
    print(f"canonical_indices: {len(canon_indices)} (not enumerated)")
    print(f"total excluded from pool: {len(excluded)}")

    available = [i for i in range(974) if i not in set(excluded)]
    print(f"available pool size: {len(available)} (974 - {len(excluded)})")

    if len(available) < N:
        print(f"ERROR: not enough available problems ({len(available)}) for n={N}", file=sys.stderr)
        return 3

    rng = random.Random(SEED)
    chosen = rng.sample(available, N)

    selected = []
    for order_idx, raw_idx in enumerate(chosen):
        p = raw[raw_idx]
        selected.append({
            "presentation_order": order_idx,
            "mbpp_index": raw_idx,
            "task_id": p["task_id"],
            "text": p["text"],
            "test_list": p["test_list"],
            "test_setup_code": p.get("test_setup_code", ""),
        })

    overlap_pilot = set(t["mbpp_index"] for t in selected) & set(pilot_indices)
    overlap_canon = set(t["mbpp_index"] for t in selected) & set(canon_indices)
    assert not overlap_pilot, f"INVARIANT VIOLATED: supplement contains pilot tasks: {overlap_pilot}"
    assert not overlap_canon, f"INVARIANT VIOLATED: supplement contains canonical tasks: {overlap_canon}"

    OUT.write_text(json.dumps({
        "schema": "ecd-mbpp-supplement-task-distribution-v1",
        "source": "MBPP (Austin et al. 2021), https://github.com/google-research/google-research/tree/master/mbpp",
        "purpose": "Top up the canonical run after the preregistered N=500 included gate was missed (8 c0 + 3 c1 exclusions in the canonical 500-trace run).",
        "total_problems_in_source": 974,
        "excluded_indices_count": len(excluded),
        "available_pool_size": len(available),
        "n_selected": N,
        "seed": SEED,
        "sampling_rule": (
            "pilot_indices = first 20 mbpp_index values from task_distribution.json; "
            "canonical_indices = all 500 mbpp_index values from task_distribution_canonical.json; "
            "available = [i for i in range(974) if i not in (pilot_indices | canonical_indices)]; "
            "supplement = random.Random(43).sample(available, 25)"
        ),
        "tasks": selected,
    }, indent=2))

    print(f"wrote {OUT}")
    print(f"  n tasks: {len(selected)}")
    print(f"  first task_id: {selected[0]['task_id']}")
    print(f"  first mbpp_index: {selected[0]['mbpp_index']}")
    print(f"  overlap with pilot: 0 (verified)")
    print(f"  overlap with canonical: 0 (verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
