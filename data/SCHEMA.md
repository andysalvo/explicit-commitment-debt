# Trace Schema (v1)

This document specifies the canonical input format for the pre-registered analysis script (`tests/preregistered_analysis.py`). The schema is **frozen** as of pre-registration. Any change requires an explicit unfreeze and a new preregistration.

## File format

- **One JSONL file per condition.** `condition_0.jsonl` for no-SRS, `condition_1.jsonl` for SRS-enforced.
- **One trace per line.** Each line is a complete JSON object satisfying the schema below.
- **No surrounding array, no commas between lines.** Pure JSONL.
- **UTF-8 encoded.**

## Trace object schema

```json
{
  "schema_version": "1",
  "trace_id": "string (unique within file)",
  "condition": 0 | 1,
  "started_at": "ISO-8601 UTC timestamp",
  "completed_at": "ISO-8601 UTC timestamp",
  "excluded": false,
  "exclusion_reason": null,
  "exclusion_timestamp": null,
  "claims": [
    {
      "id": "string (unique within trace)",
      "text": "string (the human-authored claim)",
      "authorId": "string (who made the claim)",
      "authoredAt": "ISO-8601 UTC timestamp",
      "weight": 1.0,
      "status": "UNRESOLVED" | "CONFIRMED" | "DENIED",
      "verifiedAt": "ISO-8601 UTC timestamp" | null,
      "evidence": "string (verification evidence)" | null
    }
  ]
}
```

## Field semantics

- `schema_version` — must be exactly `"1"` (string). The analysis script rejects any other value.
- `trace_id` — opaque string, unique within the file. Not used for joining; used for exclusion logging.
- `condition` — integer 0 (no SRS) or 1 (SRS enforced). Must match the condition the file is named for. The analysis script does not currently cross-check this against the filename.
- `started_at` / `completed_at` — for descriptive statistics only. Not used by the primary analysis.
- `excluded` — boolean. If `true`, the trace is removed from analysis BEFORE the Mann-Whitney U test runs. If the per-condition exclusion rate exceeds 20%, the analysis script aborts with exit code 3 and the entire run is invalidated per the preregistration.
- `exclusion_reason` — string explaining why the trace was excluded (e.g., `"network_failure"`, `"rate_limit"`, `"plane_separation_misconfigured"`). Required if `excluded == true`, `null` otherwise.
- `exclusion_timestamp` — when the exclusion was logged. Required if `excluded == true`, `null` otherwise.
- `claims` — array of claim objects in temporal order.

## Claim object semantics

- `id` — opaque string, unique within trace.
- `text` — the human-articulated claim text. **Used only for descriptive analysis and audit; not used for D computation.**
- `authorId` — who articulated the claim (a human user identifier).
- `authoredAt` — when the human made the claim.
- `weight` — evidential weight in `[0, 1]`. **In this experiment all weights are `1.0`** so D is integer-valued in practice.
- `status` — exactly one of:
  - `"UNRESOLVED"` — claim has not been discharged by deterministic verification. **Contributes `weight` to D.**
  - `"CONFIRMED"` — discharged by a deterministic verification event with status CONFIRMED. **Does not contribute to D.**
  - `"DENIED"` — verification fired and reported failure. **Does not contribute to D**, but should trigger an earned-autonomy hard reset elsewhere in the system (out of scope for the analysis script).
- `verifiedAt` — when the verification event fired. Required if status is CONFIRMED or DENIED.
- `evidence` — verification evidence string. Required if status is CONFIRMED or DENIED.

## D computation (the load-bearing calculation)

```
D(trace) = sum(c["weight"] for c in trace["claims"] if c["status"] == "UNRESOLVED")
```

This is exactly what `tests/preregistered_analysis.py::compute_D` does. Do not paraphrase or alter.

## Example trace (synthetic)

```json
{"schema_version":"1","trace_id":"trace-0001","condition":1,"started_at":"2026-04-10T12:00:00Z","completed_at":"2026-04-10T12:00:42Z","excluded":false,"exclusion_reason":null,"exclusion_timestamp":null,"claims":[{"id":"c-1","text":"Write report to /tmp/r.csv","authorId":"andy","authoredAt":"2026-04-10T12:00:01Z","weight":1.0,"status":"CONFIRMED","verifiedAt":"2026-04-10T12:00:05Z","evidence":"file exists, 4.2KB"},{"id":"c-2","text":"Deploy service to prod","authorId":"andy","authoredAt":"2026-04-10T12:00:10Z","weight":1.0,"status":"UNRESOLVED","verifiedAt":null,"evidence":null}]}
```

For this trace, D = 1.0 (one UNRESOLVED claim with weight 1.0).

## What the analysis script will NOT accept

- Files with traces that lack `schema_version` or have a different value
- Malformed JSON (script aborts with exit code 1 and reports the line number)
- Either condition with fewer than 500 included traces (script aborts with exit code 2)
- Either condition with exclusion rate > 20% (script aborts with exit code 3)
- Modifications to `tests/preregistered_analysis.py` after the OSF preregistration is timestamped (the script's self-hash changes and is recorded in the result JSON, so any modification is detectable)

## Schema versioning

If a future experiment requires a richer trace schema (e.g., per-claim provenance chains, adversarial labels, etc.), bump `schema_version` to `"2"` and write a new analysis script. The original `"1"` schema and the original analysis script remain frozen and reference the original preregistration.

## Preregistration history (schema v1)

| Version | OSF Registration | Timestamp (UTC) | Pinned analysis commit |
|---|---|---|---|
| 1 | [osf.io/az6r3](https://osf.io/az6r3/) | 2026-04-09T21:51:48 | `986423316badce6a670c84acb35f663a0353602d` |

The pinned commit's `tests/preregistered_analysis.py` has SHA-256 `0f3cf9d4512be12d618a7bf01ba0c5f7f7d2c79e919d03a05583429024c046f2`. The analysis script self-hashes its own source on every run and writes the hash into `results/canonical_result.json`, so any post-registration modification is detectable.
