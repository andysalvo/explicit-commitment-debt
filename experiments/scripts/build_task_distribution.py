#!/usr/bin/env python3
"""
Build experiments/task_distribution.json from the canonical MBPP dataset.

Sampling rule (frozen by PREREGISTRATION_ADDENDUM_001.md):
    random.Random(42).sample(range(974), 500)

The sample order is the presentation order. The same 500 problems are used in
both conditions. Run this script ONCE before the pilot. Re-running is a no-op
because the seed is fixed.

Usage:
    python experiments/scripts/build_task_distribution.py
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RAW = REPO / "experiments" / "data" / "mbpp_raw.jsonl"
OUT = REPO / "experiments" / "task_distribution.json"
N = 500
SEED = 42


def main() -> int:
    if not RAW.exists():
        print(f"ERROR: raw MBPP not found at {RAW}", file=sys.stderr)
        return 1

    raw = [json.loads(line) for line in RAW.read_text().splitlines() if line.strip()]
    if len(raw) != 974:
        print(
            f"ERROR: expected 974 MBPP problems, found {len(raw)}. "
            f"The preregistration addendum specifies the canonical 974-problem MBPP set.",
            file=sys.stderr,
        )
        return 2

    rng = random.Random(SEED)
    indices = rng.sample(range(974), N)

    selected = []
    for order_idx, raw_idx in enumerate(indices):
        p = raw[raw_idx]
        selected.append({
            "presentation_order": order_idx,
            "mbpp_index": raw_idx,
            "task_id": p["task_id"],
            "text": p["text"],
            "test_list": p["test_list"],
            "test_setup_code": p.get("test_setup_code", ""),
        })

    OUT.write_text(json.dumps({
        "schema": "ecd-mbpp-task-distribution-v1",
        "source": "MBPP (Austin et al. 2021), https://github.com/google-research/google-research/tree/master/mbpp",
        "total_problems_in_source": 974,
        "n_selected": N,
        "seed": SEED,
        "sampling_rule": "random.Random(42).sample(range(974), 500)",
        "tasks": selected,
    }, indent=2))

    print(f"wrote {OUT}")
    print(f"  n tasks: {len(selected)}")
    print(f"  first task_id: {selected[0]['task_id']}")
    print(f"  last task_id:  {selected[-1]['task_id']}")
    print(f"  first text:    {selected[0]['text'][:70]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
