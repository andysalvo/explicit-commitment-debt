#!/usr/bin/env python3
"""
Canonical run supplement — top-up dispatcher.

Filed in response to the canonical 1000-trace run hitting exit code 2 from the
preregistered analysis script (492 included in c0, 497 included in c1, both
under the N=500 included gate). This script implements the preregistered
stopping rule (OSF field 344-55: "data collection stops after exactly 500
completed, non-excluded traces per condition") by appending fresh traces drawn
from a disjoint supplementary task distribution until both conditions clear
the gate.

Method invariants (locked):
  - Imports run_one_trace from experiments/run_pilot.py UNCHANGED. Same agent
    prompts, same model (gpt-4.1-mini), same temperature (0.0), same max tokens
    (1024), same extractor prompt, same claim status mapping rule, same
    exclusion rules.
  - Reads tasks from experiments/task_distribution_supplement.json (25 fresh
    MBPP tasks, sampled from the 454-task unused pool with Random(43)).
  - APPENDS traces to data/condition_0.jsonl and data/condition_1.jsonl.
  - Uses trace_idx values starting at 500 (the canonical run used 0..499).
  - Interleaves conditions exactly like the canonical run (c0_500, c1_500,
    c0_501, c1_501, ...).
  - Aborts immediately if either output file is missing.

This script is NOT a re-run of the canonical experiment. It is a continuation
of it, dispatching the additional traces the original harness should have
dispatched per the preregistered stopping rule.

Usage:
    python experiments/run_canonical_supplement.py
"""
from __future__ import annotations
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Import the harness UNCHANGED.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_pilot import run_one_trace, now_iso, SCHEMA_VERSION  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SUPPLEMENT_DIST = REPO / "experiments" / "task_distribution_supplement.json"
C0_OUT = REPO / "data" / "condition_0.jsonl"
C1_OUT = REPO / "data" / "condition_1.jsonl"
START_TRACE_IDX = 500  # canonical run used 0..499
TRACE_ID_PREFIX = "canonical"


def main() -> int:
    if not SUPPLEMENT_DIST.exists():
        print(f"ERROR: supplement distribution not found at {SUPPLEMENT_DIST}", file=sys.stderr)
        return 1
    if not C0_OUT.exists() or not C1_OUT.exists():
        print(
            f"ERROR: canonical condition files do not exist. This script appends "
            f"to existing canonical data; it does not start a new run.\n"
            f"  {C0_OUT}\n  {C1_OUT}",
            file=sys.stderr,
        )
        return 1

    tasks = json.loads(SUPPLEMENT_DIST.read_text())["tasks"]
    print(f"Loaded {len(tasks)} supplement tasks from {SUPPLEMENT_DIST.name}")
    print(f"  c0 output (append): {C0_OUT}")
    print(f"  c1 output (append): {C1_OUT}")
    print(f"  starting trace_idx: {START_TRACE_IDX}")
    print(f"  interleaved dispatch")
    print()

    out_paths = {0: C0_OUT, 1: C1_OUT}

    # Interleaved plan: (c0, 500), (c1, 500), (c0, 501), (c1, 501), ...
    # The trace's task is tasks[i] where i = trace_idx - START_TRACE_IDX.
    plan: list[tuple[int, int]] = []
    for i in range(len(tasks)):
        plan.append((0, START_TRACE_IDX + i))
        plan.append((1, START_TRACE_IDX + i))

    print(f"=== Dispatching {len(plan)} supplement traces (interleaved) ===")
    n_done = 0
    for (condition, trace_idx) in plan:
        task = tasks[trace_idx - START_TRACE_IDX]
        t0 = time.time()
        try:
            trace = run_one_trace(task, condition, trace_idx)
        except Exception as e:
            trace = {
                "schema_version": SCHEMA_VERSION,
                "trace_id": f"{TRACE_ID_PREFIX}-c{condition}-{trace_idx:04d}",
                "condition": condition,
                "started_at": now_iso(),
                "completed_at": now_iso(),
                "excluded": True,
                "exclusion_reason": f"harness_uncaught: {type(e).__name__}: {e}",
                "exclusion_timestamp": now_iso(),
                "claims": [],
                "task_id": task["task_id"],
                "verification_result": None,
                "extracted_function_name": None,
                "agent_output": None,
            }
        # Force the canonical trace_id format.
        trace["trace_id"] = f"{TRACE_ID_PREFIX}-c{condition}-{trace_idx:04d}"

        with out_paths[condition].open("a", encoding="utf-8") as f:
            f.write(json.dumps(trace) + "\n")
        n_done += 1
        dt = time.time() - t0
        # Progress lines do not display D values (rigor).
        excl_tag = "EXCL" if trace["excluded"] else "OK"
        print(
            f"  [{n_done:>3}/{len(plan)}] c{condition} #{trace_idx:04d} "
            f"task={task['task_id']:>4} "
            f"verif={trace.get('verification_result','-'):<22} "
            f"{excl_tag}  {dt:.1f}s"
            + (f"  reason={trace.get('exclusion_reason')}" if trace["excluded"] else ""),
            flush=True,
        )

    print()
    print("supplement complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
