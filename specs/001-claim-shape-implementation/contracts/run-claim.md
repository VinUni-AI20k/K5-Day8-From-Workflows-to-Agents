# Shared `run_claim` Contract

Canonical source: `src/lab8/schemas.py`, `src/lab8/shapes/common.py`, `docs/contracts.md`.

## Callable

Each shape module exports:

```python
run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult
```

Supported shape labels are `workflow`, `single`, `orchestrator`, and the existing reference
`swarm`. Do not change the callable or `RunResult` schema.

## `RunResult`

Required fields: `run_id`, `claim_id`, `shape`, `seed`, `status`, `proposal_amount`,
`refund_effects`, `committed_audit_count`, `model_calls`, `tool_calls`, `input_tokens`,
`output_tokens`, `cost_estimate`, `trace_path`, and optional `error_reason`.

Allowed statuses: `resolved`, `needs_info`, `escalated`, `denied`, `failed`.

Run ID format: `R-{shape}-{claim_id}-s{seed}`. `proposal_amount` is an integer VND value and
represents the quote, not the capped amount the host actually writes. Prefer
`lab8.shapes.common.finish()` so ledger-derived effect/audit values and trace output are
consistent.

## Outcome Mapping

| Condition | Status | Proposal amount | Ledger/audit |
|---|---|---:|---|
| Unknown claim | `failed` | 0 | No refund |
| Missing order ID | `needs_info` | 0 | No refund |
| Missing order or order outside principal scope | `escalated` | 0 | No refund; expose no protected order fields |
| Zero quote | `denied` | 0 | No refund; do not call refund operation |
| Positive quote rejected by host | `denied` | Full quote | No refund; host records `policy_denied` |
| Positive quote accepted by host | `resolved` | Full quote | One host-capped ledger effect and committed audit |
| Different amount conflicts with a committed claim refund | `failed` | Attempted quote | Preserve prior ledger amount |

## Refund Boundary

- Only the shape/code calls `durability.issue_refund`; model decisions cannot invoke write tools.
- Pass the full deterministic quote. Do not pre-subtract prior refunds; the host calculates the
  per-order remainder transactionally.
- Pass `crash_at` unchanged. Do not catch `InjectedCrash`; caller/test controls resume.
- A successful retry for the same claim does not add another ledger entry or committed audit.

## Trace Boundary

Each normal return path writes a new JSON file in the current run. It is an object containing
matching `run_id`, `events` list, and may include `steps`. Files written by a shape alongside the
trace begin with the same `run_id`. No secret/header/PII/internal note/item name may appear in
trace, side files, or stdout. Use allowlisted tool views and sanitized handoffs rather than raw
database rows.
