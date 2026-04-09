#!/usr/bin/env python3
"""
SRS x ECD experimental harness — scaffold.

This script runs the controlled comparison described in the OSF
preregistration. It is the testbed that produces the JSONL trace files the
pre-registered analysis script consumes.

IMPORTANT: This file MUST NOT be executed at full scale until the OSF
preregistration is timestamped (Register button clicked). The data does not
exist until after preregistration. This is the core rigor rule — see
ROADMAP.md.

Status: SCAFFOLD. The full integration with a multi-LLM agent fleet is left
as a TODO. The scaffold defines the input/output contracts, the configuration
schema, the exclusion logger, and the trace writer. Replace the
`run_single_trace()` function with a real agent dispatch when the testbed is
wired up.

Usage (after preregistration is locked AND scaffold is filled in):
    python experiments/srs_ecd_experiment.py \\
        --condition 0 \\
        --n-traces 500 \\
        --output  data/condition_0.jsonl \\
        --task-distribution experiments/task_distribution.json \\
        --seed 42

After both conditions are run:
    python tests/preregistered_analysis.py \\
        --condition-0 data/condition_0.jsonl \\
        --condition-1 data/condition_1.jsonl \\
        --output      results/canonical_result.json

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_task_distribution(path: Path) -> list[dict]:
    """Load the fixed task distribution. Each task is a dict with fields:
    `task_id`, `task_text`, `expected_claim_count` (optional, for sanity)."""
    if not path.exists():
        print(f"ERROR: task distribution not found: {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def run_single_trace(
    *,
    task: dict,
    condition: int,
    trace_id: str,
    rng: random.Random,
) -> dict:
    """Run a single decision trace under the given condition.

    SCAFFOLD: replace this function body with a real call into the multi-LLM
    agent fleet. The condition value controls whether the SRS enforcer is
    active at runtime:

      condition == 0: SRS enforcer DISABLED
                      (agents may violate plane boundaries silently)
      condition == 1: SRS enforcer ENABLED
                      (plane-boundary violations throw at runtime)

    The function MUST return a dict matching `data/SCHEMA.md`. Any deviation
    will be rejected by the pre-registered analysis script.

    The current implementation is a placeholder that raises NotImplementedError
    so this scaffold cannot accidentally produce data that looks real.
    """
    raise NotImplementedError(
        "run_single_trace() is a scaffold. Replace with a real multi-LLM "
        "agent dispatch that produces a trace conforming to data/SCHEMA.md "
        "before running the experiment at scale."
    )


def write_trace(trace: dict, output: Path) -> None:
    """Append a trace to the JSONL output file."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as f:
        f.write(json.dumps(trace) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="SRS x ECD experimental harness (scaffold).",
    )
    ap.add_argument("--condition", required=True, type=int, choices=[0, 1])
    ap.add_argument("--n-traces", required=True, type=int)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--task-distribution", required=True, type=Path)
    ap.add_argument("--seed", required=True, type=int)
    ap.add_argument(
        "--allow-scaffold",
        action="store_true",
        help="Required to run while run_single_trace is still a scaffold. "
        "Without this flag the script refuses to run.",
    )
    args = ap.parse_args()

    if not args.allow_scaffold:
        print(
            "REFUSING TO RUN: this script is a scaffold. The "
            "run_single_trace() function is not yet wired to a real agent "
            "dispatch. Wire it up first, then re-run with "
            "--allow-scaffold to confirm you understand it is now "
            "producing real data.",
            file=sys.stderr,
        )
        return 1

    print(f"Running experiment: condition={args.condition}, n={args.n_traces}")
    print(f"  task distribution: {args.task_distribution}")
    print(f"  output:            {args.output}")
    print(f"  seed:              {args.seed}")
    print()

    tasks = load_task_distribution(args.task_distribution)
    rng = random.Random(args.seed)
    rng.shuffle(tasks)

    # Truncate output file at start; this is a fresh run.
    if args.output.exists():
        print(
            f"WARNING: output file already exists, refusing to overwrite: "
            f"{args.output}",
            file=sys.stderr,
        )
        return 2

    completed = 0
    excluded = 0
    for i in range(args.n_traces):
        task = tasks[i % len(tasks)]
        trace_id = f"c{args.condition}-{i:05d}"
        try:
            trace = run_single_trace(
                task=task,
                condition=args.condition,
                trace_id=trace_id,
                rng=rng,
            )
        except NotImplementedError:
            raise
        except Exception as e:
            # Per the preregistration, any system error excludes the trace.
            trace = {
                "schema_version": SCHEMA_VERSION,
                "trace_id": trace_id,
                "condition": args.condition,
                "started_at": now_iso(),
                "completed_at": now_iso(),
                "excluded": True,
                "exclusion_reason": f"system_error: {type(e).__name__}: {e}",
                "exclusion_timestamp": now_iso(),
                "claims": [],
            }
            excluded += 1

        write_trace(trace, args.output)
        completed += 1
        if completed % 50 == 0:
            print(
                f"  ...{completed}/{args.n_traces} written "
                f"({excluded} excluded so far)",
                flush=True,
            )

        # Per the preregistration: if exclusion rate exceeds 20% mid-run,
        # invalidate the entire run and restart from zero.
        if completed >= 100 and excluded / completed > 0.20:
            print(
                f"ABORT: exclusion rate {excluded / completed:.2%} exceeds "
                f"20%. Per the preregistration, this run is invalidated. "
                f"Discard {args.output} and restart from zero.",
                file=sys.stderr,
            )
            return 3

    print()
    print(f"  done: {completed} traces written, {excluded} excluded")
    print(f"  output: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
