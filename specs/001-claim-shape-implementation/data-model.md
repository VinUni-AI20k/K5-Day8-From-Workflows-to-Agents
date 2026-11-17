# Data Model: Claim Shape Implementation

This design reuses the existing SQLite world and Python dataclasses. It introduces no tables,
columns, or persisted application entities.

## Runtime Entities

### Claim

- **Identity**: `claim_id`.
- **Relevant fields**: `principal_id`, optional `order_id`, untrusted `ticket`, optional
  `approval_id`.
- **Sensitive fields**: `parent_secret`, `raw_headers_json`; these are never passed to an
  investigator or emitted in trace/output.
- **Relations**: references the authoritative order and its approval selection.
- **Validation**: a missing claim yields `failed` with proposal amount `0`; missing `order_id`
  yields `needs_info` and no refund.

### Order view

- **Identity**: `order_id`; ownership is scoped by `principal_id`.
- **Allowlisted fields** (`tools.ORDER_FIELDS`): `order_id`, `status`, `delay_days`,
  `shipping_fee_vnd`, `paid_vnd`, `damage_verified`, `carrier`.
- **Withheld fields**: phone, address, internal note, item name, and any unapproved database
  fields.
- **Validation**: missing or non-owned order is not visible; shape returns the contract-defined
  escalation outcome without copying protected values.

### Policy and clause

- **Identity**: policy `policy_id` and clause IDs.
- **Relevant fields**: version, `is_current`, `effective_date`, supersession metadata, clauses.
- **Validation**: only current policies effective on the configured as-of date establish an
  entitlement; historical clauses may be returned by `get_clause` and must not be treated as
  current by a shape.

### Quote

- **Fields**: integer `amount_vnd`, reason, clause IDs, and per-clause parts.
- **Validation**: deterministic compensation from structured order and policy data; when multiple
  eligible clauses apply, amount is the greatest eligible amount, not their sum. The full quote
  is passed to the host; the host applies approval, paid amount, and per-order remaining cap.

### Approval

- **Identity**: `approval_id`; associated `claim_id`.
- **Relevant fields**: `approved_vnd`, status, expiry.
- **Validation**: host requires a valid, active, positive approval bound to the claim. Shape does
  not synthesize or bypass approval.

### Refund ledger effect and audit

- **Identity**: one ledger entry per claim, with idempotency key `refund:{claim_id}`.
- **Fields**: claim/order IDs, committed `amount_vnd`, status; audit contains `refund_committed`
  event and host decision details.
- **Validation**: transaction and host enforce the amount and order cap; same-claim replay does not
  add a second effect; conflicting amount leaves the committed effect unchanged. A post-effect
  crash/resume leaves one effect and one committed audit.

### Budget

- **Fields**: model/tool call counts, input/output tokens, estimated cost, steps.
- **Validation**: all shape actions that use model/tool adapters update the shared `Budget`; the
  single-agent shape stops after at most eight ReAct steps.

### RunResult

- **Identity**: `run_id = R-{shape}-{claim_id}-s{seed}`, `claim_id`, `shape`, `seed`.
- **Outcome fields**: status, integer `proposal_amount`, refund effects, committed audit count,
  budget metrics, trace path, optional error reason.
- **Status set**: `resolved`, `needs_info`, `escalated`, `denied`, `failed`.
- **Validation**: status must belong to the defined set; claim identity and run identity must match
  the invocation; `proposal_amount` is the full quote (not host net amount) when the quote is
  positive and reached the host.

### Trace

- **Fields**: `run_id`, `steps`, and `events`; every event contains a kind and payload.
- **Validation**: a fresh JSON file is written during the current run; `run_id` matches the
  result; `events` is a list. No secret, header, phone, address, internal note, or item name may
  appear in trace, same-run side files, or stdout.

### Handoff (`handoff.v1`)

- **Allowed top-level fields**: `contract_version`, `request_id`, `claim_id`, `principal_scope`,
  `task`, `facts`, `allowed_tools`, `max_output_tokens`.
- **Allowed facts**: `delay_days`, `damage_verified`, `carrier`, `order_status`,
  `shipping_fee_vnd`, `paid_vnd`.
- **Validation**: `allowed_tools` is a subset of `READONLY_TOOLS`; no raw parent context, secrets,
  or write tools are forwarded.

## Persistence and State Transitions

The existing tables are defined in `src/lab8/db.py`: `claims`, `orders`, `policies`, `approvals`,
`refund_ledger`, `audit_events`, and `checkpoints`. Shape work MUST NOT alter this schema.

Refund flow: quote absent/zero → no write; positive quote → host authorization → either denied
with policy audit or one committed ledger effect plus one committed audit → optional checkpoint.
An injected crash after the effect and before checkpoint is resumed through the existing ledger
and idempotency path, not a new persistence protocol.
