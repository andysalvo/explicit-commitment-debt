#!/usr/bin/env python3
"""
Build experiments/task_distribution_canonical.json — the task set used in the
canonical 1000-trace run.

Sampling rule (frozen by Phase-3 fix commit):
    pilot_indices = first 20 mbpp_index values from task_distribution.json
    available     = [i for i in range(974) if i not in pilot_indices]
    canonical     = random.Random(42).sample(available, 500)

This guarantees:
  - The canonical run uses 500 MBPP problems disjoint from the 20 pilot problems.
  - The seed is still 42 (reproducible).
  - The pool excludes only the literal pilot tasks; everything else is fair game.
  - Re-running this script always produces the same file.

Run ONCE before the canonical experiment. The output file is committed.

Usage:
    python experiments/scripts/build_canonical_task_distribution.py
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RAW = REPO / "experiments" / "data" / "mbpp_raw.jsonl"
PILOT_DIST = REPO / "experiments" / "task_distribution.json"
OUT = REPO / "experiments" / "task_distribution_canonical.json"
N = 500
SEED = 42


def main() -> int:
    if not RAW.exists():
        print(f"ERROR: raw MBPP not found at {RAW}", file=sys.stderr)
        return 1
    if not PILOT_DIST.exists():
        print(f"ERROR: pilot task distribution not found at {PILOT_DIST}", file=sys.stderr)
        return 1

    raw = [json.loads(line) for line in RAW.read_text().splitlines() if line.strip()]
    if len(raw) != 974:
        print(f"ERROR: expected 974 MBPP problems, found {len(raw)}", file=sys.stderr)
        return 2

    pilot = json.loads(PILOT_DIST.read_text())
    pilot_indices = sorted({t["mbpp_index"] for t in pilot["tasks"][:20]})
    print(f"pilot mbpp_indices excluded ({len(pilot_indices)}): {pilot_indices}")

    available = [i for i in range(974) if i not in set(pilot_indices)]
    print(f"available pool size: {len(available)} (974 - {len(pilot_indices)})")

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

    overlap = set(t["mbpp_index"] for t in selected) & set(pilot_indices)
    assert not overlap, f"INVARIANT VIOLATED: canonical contains pilot tasks: {overlap}"

    OUT.write_text(json.dumps({
        "schema": "ecd-mbpp-canonical-task-distribution-v1",
        "source": "MBPP (Austin et al. 2021), https://github.com/google-research/google-research/tree/master/mbpp",
        "total_problems_in_source": 974,
        "pilot_indices_excluded": pilot_indices,
        "available_pool_size": len(available),
        "n_selected": N,
        "seed": SEED,
        "sampling_rule": (
            "pilot_indices = first 20 mbpp_index values from task_distribution.json; "
            "available = [i for i in range(974) if i not in pilot_indices]; "
            "canonical = random.Random(42).sample(available, 500)"
        ),
        "tasks": selected,
    }, indent=2))

    print(f"wrote {OUT}")
    print(f"  n tasks: {len(selected)}")
    print(f"  first task_id: {selected[0]['task_id']}")
    print(f"  first mbpp_index: {selected[0]['mbpp_index']}")
    print(f"  overlap with pilot: {len(overlap)} (must be 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
