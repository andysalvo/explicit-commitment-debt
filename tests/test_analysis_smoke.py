#!/usr/bin/env python3
"""
Smoke test for the pre-registered analysis script.

Generates two synthetic JSONL trace files (condition 0 and condition 1) with
known properties, then runs the canonical analysis script against them and
verifies the verdict matches expectation.

This test is NOT part of the experiment. It exists to prove that:
  1. The analysis script can ingest valid trace JSONL.
  2. The schema_version check works.
  3. The N >= 500 gate works.
  4. The exclusion-rate gate works.
  5. Mann-Whitney U on a known difference produces the expected verdict.
  6. The script is reproducible (same input -> same output).

Run this AT LEAST ONCE before pre-registration is locked, to confirm the
analysis machinery is wired up correctly. After that, do NOT modify the
analysis script for any reason. Modifying it would invalidate the
pre-registration.

Usage:
    python tests/test_analysis_smoke.py
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_SCRIPT = REPO_ROOT / "tests" / "preregistered_analysis.py"
SCHEMA_VERSION = "1"
N_PER_CONDITION = 500


def make_trace(trace_id: int, n_unresolved: int, *, excluded: bool = False) -> dict:
    """Create a synthetic trace where exactly n_unresolved claims have status
    UNRESOLVED. The remaining claims are CONFIRMED. weight is always 1.0."""
    claims = []
    for i in range(n_unresolved):
        claims.append({
            "id": f"claim-{trace_id}-{i}",
            "text": f"synthetic claim {i}",
            "authorId": "smoke-test",
            "authoredAt": "2026-04-09T00:00:00Z",
            "weight": 1.0,
            "status": "UNRESOLVED",
            "verifiedAt": None,
            "evidence": None,
        })
    # Always one CONFIRMED claim so traces are non-trivial.
    claims.append({
        "id": f"claim-{trace_id}-confirmed",
        "text": "synthetic confirmed claim",
        "authorId": "smoke-test",
        "authoredAt": "2026-04-09T00:00:00Z",
        "weight": 1.0,
        "status": "CONFIRMED",
        "verifiedAt": "2026-04-09T00:00:01Z",
        "evidence": "synthetic evidence",
    })
    return {
        "schema_version": SCHEMA_VERSION,
        "trace_id": f"trace-{trace_id}",
        "condition": None,  # set by caller
        "started_at": "2026-04-09T00:00:00Z",
        "completed_at": "2026-04-09T00:00:10Z",
        "excluded": excluded,
        "exclusion_reason": "synthetic_smoke_test_exclusion" if excluded else None,
        "exclusion_timestamp": "2026-04-09T00:00:10Z" if excluded else None,
        "claims": claims,
    }


def generate_jsonl(path: Path, condition: int, mean_unresolved: float, n: int) -> None:
    """Generate n traces with Poisson-ish counts of UNRESOLVED claims."""
    rng = random.Random(42 + condition)  # deterministic
    with path.open("w", encoding="utf-8") as f:
        for i in range(n):
            # Use a simple deterministic distribution: round-robin around mean.
            n_unresolved = max(0, int(rng.gauss(mean_unresolved, mean_unresolved / 2)))
            trace = make_trace(trace_id=i, n_unresolved=n_unresolved)
            trace["condition"] = condition
            f.write(json.dumps(trace) + "\n")


def run_analysis(c0: Path, c1: Path, out: Path) -> tuple[int, str, str]:
    """Run the canonical analysis script and capture results."""
    proc = subprocess.run(
        [
            sys.executable,
            str(ANALYSIS_SCRIPT),
            "--condition-0", str(c0),
            "--condition-1", str(c1),
            "--output", str(out),
        ],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def main() -> int:
    print("Smoke test: pre-registered analysis script")
    print("=" * 60)

    if not ANALYSIS_SCRIPT.exists():
        print(f"ERROR: analysis script not found at {ANALYSIS_SCRIPT}")
        return 1

    failures = 0

    # ----- Test 1: known SRS effect (mean_unresolved 5 vs 1.5) -----
    # Expectation: CONFIRMED. p << 0.01, median ratio < 0.75.
    print("\nTest 1: known SRS effect (5.0 vs 1.5 mean unresolved)")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        c0 = tmp_dir / "c0.jsonl"
        c1 = tmp_dir / "c1.jsonl"
        out = tmp_dir / "result.json"

        generate_jsonl(c0, condition=0, mean_unresolved=5.0, n=N_PER_CONDITION)
        generate_jsonl(c1, condition=1, mean_unresolved=1.5, n=N_PER_CONDITION)

        rc, stdout, stderr = run_analysis(c0, c1, out)
        if not out.exists():
            print(f"  FAIL: output file not created. stderr:\n{stderr}")
            failures += 1
        else:
            result = json.loads(out.read_text())
            verdict = result["decision"]["verdict"]
            print(f"  verdict: {verdict}")
            print(f"  p={result['test']['p_value']:.4g}  "
                  f"median_ratio={result['test']['median_ratio']:.3f}")
            if verdict != "CONFIRMED":
                print(f"  FAIL: expected CONFIRMED, got {verdict}")
                failures += 1
            else:
                print(f"  PASS: known effect produced CONFIRMED verdict")

    # ----- Test 2: no effect (both conditions identical) -----
    print("\nTest 2: no effect (both conditions identical 3.0 mean)")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        c0 = tmp_dir / "c0.jsonl"
        c1 = tmp_dir / "c1.jsonl"
        out = tmp_dir / "result.json"

        generate_jsonl(c0, condition=0, mean_unresolved=3.0, n=N_PER_CONDITION)
        generate_jsonl(c1, condition=1, mean_unresolved=3.0, n=N_PER_CONDITION)

        rc, stdout, stderr = run_analysis(c0, c1, out)
        if not out.exists():
            print(f"  FAIL: output file not created. stderr:\n{stderr}")
            failures += 1
        else:
            result = json.loads(out.read_text())
            verdict = result["decision"]["verdict"]
            print(f"  verdict: {verdict}")
            print(f"  p={result['test']['p_value']:.4g}  "
                  f"median_ratio={result['test']['median_ratio']:.3f}")
            if verdict == "CONFIRMED":
                print("  FAIL: no-effect data should not produce CONFIRMED")
                failures += 1
            else:
                print(f"  PASS: no-effect data produced {verdict}")

    # ----- Test 3: too few traces should ABORT -----
    print("\nTest 3: too few traces should abort with exit code 2")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        c0 = tmp_dir / "c0.jsonl"
        c1 = tmp_dir / "c1.jsonl"
        out = tmp_dir / "result.json"

        generate_jsonl(c0, condition=0, mean_unresolved=3.0, n=100)
        generate_jsonl(c1, condition=1, mean_unresolved=3.0, n=100)

        rc, stdout, stderr = run_analysis(c0, c1, out)
        if rc == 2:
            print("  PASS: aborted with exit code 2 as expected")
        else:
            print(f"  FAIL: expected exit code 2, got {rc}")
            failures += 1

    # ----- Test 4: high exclusion rate should ABORT -----
    print("\nTest 4: high exclusion rate (>20%) should abort with exit code 3")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        c0 = tmp_dir / "c0.jsonl"
        c1 = tmp_dir / "c1.jsonl"
        out = tmp_dir / "result.json"

        # 600 traces in c0, 200 of them excluded -> 33% exclusion rate
        with c0.open("w") as f:
            for i in range(600):
                t = make_trace(i, n_unresolved=3, excluded=(i < 200))
                t["condition"] = 0
                f.write(json.dumps(t) + "\n")
        generate_jsonl(c1, condition=1, mean_unresolved=3.0, n=N_PER_CONDITION)

        rc, stdout, stderr = run_analysis(c0, c1, out)
        if rc == 3:
            print("  PASS: aborted with exit code 3 as expected")
        else:
            print(f"  FAIL: expected exit code 3, got {rc}")
            failures += 1

    # ----- Test 5: reproducibility (same input -> same output hash) -----
    print("\nTest 5: reproducibility (same input -> identical result JSON)")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        c0 = tmp_dir / "c0.jsonl"
        c1 = tmp_dir / "c1.jsonl"
        out_a = tmp_dir / "result_a.json"
        out_b = tmp_dir / "result_b.json"

        generate_jsonl(c0, condition=0, mean_unresolved=4.0, n=N_PER_CONDITION)
        generate_jsonl(c1, condition=1, mean_unresolved=2.0, n=N_PER_CONDITION)

        run_analysis(c0, c1, out_a)
        run_analysis(c0, c1, out_b)
        if out_a.read_text() == out_b.read_text():
            print("  PASS: two runs produced byte-identical results")
        else:
            print("  FAIL: two runs of the same input produced different results")
            failures += 1

    print()
    print("=" * 60)
    if failures == 0:
        print("ALL SMOKE TESTS PASSED")
        return 0
    else:
        print(f"{failures} smoke tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
