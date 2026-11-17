# Feature Specification: Claim Shape Implementation

**Feature Branch**: `001-claim-shape-implementation`

**Created**: 2026-11-16

**Status**: Draft

**Input**: User description: Create a specification from repository requirements and the prior requirement matrix. Preserve source meaning, identify existing and missing code, and group work into independently implementable features.

## User Scenarios & Testing

### User Story 1 - Implement the Workflow Shape (Priority: P1, Must-have)

As a project team member, I can complete the fixed-step workflow shape so that it processes claims according to the assignment's shared contract and business rules.

**Requirement IDs**: M-01, M-02, M-03, M-04, M-05, M-06, M-07

**Why this priority**: This is one of the three required student implementations and must be available for the required comparison.

**Independent Test**: Run the workflow student tests and applicable public contract/business-rule tests for normal, denied, repeated, and crash/resume claim runs.

**Acceptance Scenarios**:

1. **Given** a claim with a valid order, current policy, and valid approval, **When** the workflow processes it, **Then** code computes the compensation and sends the full quote to the host refund gate; the returned result and ledger reflect the host decision.
2. **Given** a missing order ID, unavailable or unowned order, or zero quote, **When** the workflow processes the claim, **Then** it returns the contract-defined status and amount without creating a refund.
3. **Given** an invalid approval or a quote rejected by host policy, **When** the workflow processes the claim, **Then** it creates no refund and a positive quote rejected by the host produces the required `policy_denied` audit.
4. **Given** shipping and verified-damage entitlements are both applicable, **When** compensation is computed, **Then** the quote uses the greater eligible amount rather than their sum.
5. **Given** a repeated claim or a crash at the refund boundary, **When** the run is repeated or resumed, **Then** the committed refund is not duplicated, a conflicting amount does not replace the committed amount, and `InjectedCrash` is not swallowed.
6. **Given** any success or early-exit path, **When** the run completes, **Then** it returns a valid `RunResult` and a fresh trace JSON whose `run_id` matches the result and whose `events` value is a list, without exposing protected data.

**Existing in codebase**: The workflow module, shared result/trace/host support, public tests, and reference shape exist.

**Missing**: `src/lab8/shapes/workflow.py` currently returns `not_implemented` and does not implement the required behavior.

---

### User Story 2 - Implement the Single-Agent Shape (Priority: P1, Must-have)

As a project team member, I can complete the single-agent shape so that the model can select among permitted read operations while code retains policy, compensation, and refund authority.

**Requirement IDs**: M-01, M-02, M-03, M-04, M-05, M-06, M-07

**Why this priority**: This is one of the three required student implementations and is needed for the four-shape comparison.

**Independent Test**: Run the single-agent student tests and applicable public contract/business-rule tests, including the specified ReAct step limit and refund/crash cases.

**Acceptance Scenarios**:

1. **Given** a claim to investigate, **When** the model selects an action, **Then** it can select only permitted read tools and the ReAct loop uses no more than 8 steps.
2. **Given** sufficient claim, order, policy, and approval data, **When** the run reaches a refund decision, **Then** code computes compensation and calls the host with the full quote; the model does not determine the amount or commit a refund.
3. **Given** missing or invalid data, an ineligible claim, or rejected approval, **When** the run ends, **Then** it returns the contract-defined status/amount and creates no unauthorized refund; positive host-denied quotes are audited by the host.
4. **Given** a repeated claim or a crash at the refund boundary, **When** the claim is retried or resumed, **Then** the host's idempotency and crash behavior leave at most one refund and one committed audit.
5. **Given** any success or early-exit path, **When** the run completes, **Then** it returns a valid result and fresh contract-compliant trace without protected data.

**Existing in codebase**: Shared host, MockLLM, read tools, contracts, tests, and reference shape are available.

**Missing**: `src/lab8/shapes/single.py` currently returns `not_implemented` and does not implement the required behavior.

---

### User Story 3 - Implement the Orchestrator Shape (Priority: P1, Must-have)

As a project team member, I can complete the orchestrator and investigator shape so that investigation can be delegated without exposing disallowed data or write capability.

**Requirement IDs**: M-01, M-02, M-03, M-04, M-05, M-06, M-07, M-08

**Why this priority**: This is one of the three required student implementations; safe handoff is also an explicit graded requirement.

**Independent Test**: Run orchestrator student tests for claim outcomes, handoff allowlisting, investigator read-only access, trace safety, and refund/crash behavior.

**Acceptance Scenarios**:

1. **Given** an orchestrator delegates an investigation, **When** it creates the handoff, **Then** the handoff contains only allowlisted, sanitized fields and the investigator receives no raw claim or parent context, secrets, or write capability.
2. **Given** an investigator performs its work, **When** it accesses tools, **Then** available operations are read-only.
3. **Given** the investigated claim is eligible, **When** a refund is proposed, **Then** code computes compensation and the orchestrator passes the full quote to the host; the model/investigator does not commit or determine the refund.
4. **Given** the claim is ineligible, lacks valid approval, or host policy rejects its quote, **When** processing finishes, **Then** the contract-defined result is returned and no unauthorized refund is recorded; positive rejected quotes have the required host audit.
5. **Given** a repeated claim or injected crash, **When** the run is repeated or resumed, **Then** no duplicate refund is committed and the injected crash is propagated as specified.
6. **Given** any success or early-exit path, **When** the run completes, **Then** it returns a valid result and fresh trace satisfying the trace contract and containing no protected data.

**Existing in codebase**: Handoff/sanitizer, read-only support, shared host and trace support, tests, and reference shape are present.

**Missing**: `src/lab8/shapes/orchestrator.py` currently returns `not_implemented`; its orchestration and investigator behavior is not implemented.

---

### User Story 4 - Verify and Submit the Required Work (Priority: P1, Must-have)

As a project team, we can verify the required shape, safety, reproducibility, and submission outcomes and support the architecture decision with generated evidence.

**Requirement IDs**: M-09, M-10, M-11, M-12, M-13

**Why this priority**: These checks and deliverables are explicitly required for passing, grading, and submitting the assignment; they do not replace shape implementation.

**Independent Test**: Run the documented tests, benchmark, crash suite, and submission checker; inspect the required reports and group/member deliverables against the source checklist.

**Acceptance Scenarios**:

1. **Given** the required implementations, **When** the public test command is run, **Then** `python -m pytest -q` passes and the protected host/config/data/measurement files and generated report JSON have not been altered contrary to assignment rules.
2. **Given** all four shapes and the public corpus, **When** the prescribed benchmark runs, **Then** the generated benchmark evidence covers at least 10 public claims and seeds `11,22,33,44,55` for all four shapes.
3. **Given** the selected shape, **When** the crash suite runs, **Then** crash safety is `20/20`; when the instructor hidden grader runs the selected shape, its pass rate is at least `0.75` across 40 claims and 5 seeds, with the three must-pass conditions satisfied.
4. **Given** benchmark and crash reports, **When** the team writes its architecture decision and research card, **Then** the ADR cites the selected shape, commit hash, run ID, report-derived numbers, and evidence limitations; the required research card fields are completed.
5. **Given** the completed submission, **When** `python -m lab8.check_submission` runs, **Then** it reports `0 FAIL` and all required team, group, ADR, research-card, and member reports have the prescribed names and required labels.
6. **Given** the team uses external material or AI tools, **When** it submits, **Then** sources, contributions, tool use, and verification are disclosed as required; no fabricated measurements, secrets, real-model API use, prohibited copying, or ticket-as-instruction behavior is present.

**Existing in codebase**: Test suite, benchmark/crash/checker tooling, report templates, rules, rubric, and submission instructions exist.

**Missing**: Completion evidence and final reports are not established by source inspection; tests and grading commands have not been run as part of this specification. Submission compliance remains to be completed by the team.

---

### User Story 5 - Complete an Optional Bonus Topic (Priority: P3, Bonus)

As a project team that has completed all required work, we can optionally complete one registered bonus topic and provide its required evidence.

**Requirement IDs**: O-01

**Why this priority**: The source explicitly makes bonus optional and allows it only after the must-pass and baseline test conditions are satisfied.

**Independent Test**: For the selected B1-B7 topic, run its tests and produce the specified report/evidence; verify the selected shape meets all must-pass conditions, hidden pass rate is at least `0.80`, and `python -m pytest -q` remains green.

**Acceptance Scenarios**:

1. **Given** required work is complete and the group has selected/registered a bonus topic, **When** that topic is submitted, **Then** it includes code, tests, report, and evidence required by the rubric.
2. **Given** any prerequisite must-pass, hidden pass-rate, or baseline test condition is unmet, **When** bonus eligibility is assessed, **Then** bonus credit is not counted.

**Existing in codebase**: Bonus topic descriptions and submission conventions exist.

**Missing**: No selected bonus topic or implementation is specified; bonus work is not required.

---

### Optional Source-Allowlisted Capabilities

These are explicitly optional in repository documentation and are not required for completion. They are not additional scope unless the team elects to use them.

- **O-02 (Should-have only if selected)**: Optional hidden self-check report; official hidden grading remains instructor-side. Existing: report instructions. Missing: optional generated report has not been verified.
- **O-03 (Should-have only if selected)**: The workflow model may draft customer response text. Existing: shape guidance. Missing: no implementation requirement unless selected.
- **O-04 (Should-have only if selected)**: A custom tracer may be used if it satisfies the existing trace contract. Existing: trace library and contract. Missing: no custom tracer is required.

### Edge Cases

- A ticket contains an order ID or policy instruction not supported by authoritative order/policy data; processing MUST use the authoritative data and MUST NOT treat ticket text as instructions.
- A policy clause is obsolete or not yet effective; it MUST NOT establish eligibility.
- Approval is absent, expired, revoked, non-positive, or references a different claim; no refund is committed and positive host-rejected quotes receive the required audit.
- The order has already received a refund from another claim; the per-order entitlement cap applies, including only the remaining difference when a new eligible entitlement is greater.
- A repeated claim requests a different amount after a refund was committed; the prior committed amount remains unchanged and the conflict follows the defined result contract.
- A run exits early or crashes after the refund effect but before its checkpoint; traces remain fresh and safe, and resuming does not duplicate the refund or committed audit.
- An order is missing or belongs to another principal; the result follows the contract without exposing phone, address, product name, or internal note.

## Requirements

### Functional Requirements

- **M-01**: The team MUST implement shapes A `workflow`, B `single`, and C `orchestrator`, preserving the shared `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult` contract.
- **M-02**: In every shape, code/host MUST control compensation, policy/eligibility, approval, and refund writing; the model MUST NOT determine the refund amount or commit a refund. Model calls MUST use the provided MockLLM as required by the assignment.
- **M-03**: Shapes MUST use order and current/effective policy data rather than ticket assertions, enforce the specified approval/payment/order-entitlement limits, and use the greater eligible amount rather than summing simultaneous shipping and damage entitlements.
- **M-04**: Shapes MUST return the contract-defined outcomes for missing order ID, missing/unowned order, zero quote, and invalid/rejected approval; a positive quote rejected by host MUST pass through the host to create the required `policy_denied` audit.
- **M-05**: Shapes MUST pass the full quote to the host refund gate. Repeated same-claim calls MUST be idempotent, and an amount conflicting with a committed refund MUST NOT replace the committed amount.
- **M-06**: Shapes MUST pass `crash_at` to the host refund operation and MUST NOT catch `InjectedCrash`; after an injected post-effect crash and resume, there MUST be exactly one refund and one `refund_committed` audit.
- **M-07**: Every path MUST return a valid result and a fresh trace JSON with matching run ID and an `events` list; trace and same-run outputs MUST not expose secret or personal/internal data.
- **M-08**: Orchestrator handoffs MUST use the documented allowlist/sanitizer; investigators MUST have read-only tools and MUST NOT receive raw claim/parent context, secrets, or write capability.
- **M-09**: The required test command MUST pass; protected measurement, host, configuration, and data files MUST remain unmodified as prohibited by the assignment; generated report JSON MUST NOT be hand-edited.
- **M-10**: The team MUST generate the prescribed benchmark for all four shapes, at least 10 public claims, and seeds `11,22,33,44,55`, plus the prescribed crash report.
- **M-11**: The team MUST select a shape using measured evidence and submit an ADR with shape, commit hash, run ID, report-derived numbers, evidence limitations, and the completed research card and reports required by the rubric.
- **M-12**: The submission MUST use prescribed names/layout, pass `python -m lab8.check_submission` with `0 FAIL`, be pushed and accessible to graders, and be submitted by each member through the specified LMS process.
- **M-13**: The team MUST follow the assignment's integrity/security rules: no real-model API or committed secrets, no treating ticket text as instructions, no copying the reference weakness, and required attribution/contribution disclosure.
- **O-01 (Bonus)**: If chosen, one B1-B7 topic MUST include the code, tests, report, and evidence specified by the rubric, and is eligible only after all stated prerequisites pass, including hidden pass rate of at least `0.80`.
- **O-02 (Optional)**: The team MAY generate the optional hidden self-check; it does not replace instructor-side hidden grading.
- **O-03 (Optional)**: The workflow MAY use the model to draft response text; this is not required.
- **O-04 (Optional)**: The team MAY use a custom tracer if its output satisfies the trace contract.

### Requirement Traceability Matrix

The source column identifies the authoritative repository material. Status reflects repository
inspection; it does not claim test execution.

| Requirement ID | Source requirement | Verifiable acceptance summary | Current status |
|---|---|---|---|
| M-01 | `README.md`; `RUBRIC.md` | All three required shapes implement the shared `run_claim` contract. | Missing: all three modules are stubs returning `not_implemented`. |
| M-02 | `README.md`; `RULES.md`; `docs/architecture.md` | Code/host owns amount, policy, approval, and refund; model uses MockLLM and cannot decide/commit refund. | Support exists; integration in the three student shapes is missing. |
| M-03 | `docs/business_rules.md` | Current policy and authoritative order data govern eligibility; approval/caps apply; overlapping shipping/damage uses the greater entitlement. | Rules and host support exist; student shape behavior is missing. |
| M-04 | `docs/business_rules.md`; `docs/contracts.md` | Missing/invalid conditions return specified result without refund; positive quote denied by host creates `policy_denied`. | Contract and host support exist; student shape behavior is missing. |
| M-05 | `docs/business_rules.md`; `docs/contracts.md` | Full quote reaches host; retries are idempotent; conflicting amount does not replace committed amount. | Host support exists; student shape integration is missing. |
| M-06 | `docs/business_rules.md`; `docs/contracts.md`; `RUBRIC.md` | Crash injection propagates; crash/resume leaves one refund and one committed audit. | Host support exists; student shape integration and crash evidence are unverified. |
| M-07 | `docs/contracts.md`; `RUBRIC.md` | Every result has a fresh valid trace with matching run ID/events; no protected data leaks. | Shared trace support exists; student shape compliance is missing/unverified. |
| M-08 | `docs/architecture.md`; `docs/contracts.md`; `RUBRIC.md` | Handoff is allowlisted/sanitized; investigator has read-only tools and no forbidden context or write access. | Handoff support exists; orchestrator implementation is missing. |
| M-09 | `README.md`; `RULES.md`; `RUBRIC.md`; `SUBMISSION.md` | Required tests pass and protected files/generated report JSON follow integrity rules. | Test suite/tools exist; current test result and final integrity check are unverified. |
| M-10 | `RUBRIC.md`; `SUBMISSION.md`; `src/reports/README.md` | Generated benchmark covers four shapes, at least 10 public claims, seeds `11,22,33,44,55`; crash report is generated. | Tooling exists; reports have not been verified. |
| M-11 | `RUBRIC.md`; `SUBMISSION.md`; `CHECKPOINTS.md` | Evidence-based shape decision and complete ADR/research/group/member reports meet required fields. | Templates/instructions exist; completed evidence and reports are unverified. |
| M-12 | `SUBMISSION.md`; `RUBRIC.md` | Prescribed layout and checker `0 FAIL`; accessible pushed repository and per-member LMS submission. | Instructions/checker exist; submission state is unverified. |
| M-13 | `RULES.md`; `RUBRIC.md` | No real-model API/secrets, instruction injection, prohibited copying, or missing attribution/contribution disclosure. | Rules exist; compliance is not verifiable from the current implementation status. |
| O-01 | `RUBRIC.md`; `docs/bonus_topics.md` | If selected, one bonus topic has code/tests/report/evidence and passes prerequisites, including hidden `>= 0.80`. | Optional; no topic selection or implementation is verified. |
| O-02 | `src/reports/README.md`; `SUBMISSION.md` | Optional self-check report may be generated; it does not replace instructor hidden grading. | Optional tooling/instructions exist; output unverified. |
| O-03 | `src/lab8/shapes/workflow.py` guidance | Workflow may draft response text; not required. | Optional, not implemented/verified. |
| O-04 | `docs/contracts.md` | Custom tracer, if used, satisfies trace contract. | Optional; default trace support exists; no custom tracer required. |

### Key Entities

- **Claim**: The assigned synthetic claim, identified by `claim_id`, associated with an order and approval reference.
- **Order**: The source-of-truth order record used to establish ownership, state, payment, shipping fee, and refund entitlement.
- **Policy**: A policy clause with current/effective status used to determine eligibility and compensation.
- **Approval**: Authorization associated with a claim and an approved amount; the host validates it before a refund.
- **Quote**: The full compensation amount proposed by code before host enforcement of approval and order-level caps.
- **Refund ledger entry**: Durable refund effect keyed for idempotent claim processing.
- **Run result and trace**: The contract-defined result and per-run event record evaluated by tests/grader.
- **Benchmark/crash evidence**: Generated reports used to verify behavior and support the architecture decision.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All three student shapes satisfy their student test matrix and return contract-valid results for tested cases.
- **SC-002**: For the selected shape, approval bypass count is `0`, secret leak count is `0`, and crash safety is `20/20`.
- **SC-003**: The instructor hidden evaluation of the selected shape achieves pass rate `>= 0.75` across 40 claims and 5 seeds.
- **SC-004**: The benchmark report covers 4 shapes, at least 10 public claims, and seeds `11,22,33,44,55`.
- **SC-005**: `python -m pytest -q` passes and `python -m lab8.check_submission` reports `0 FAIL` at submission.
- **SC-006**: The architecture decision contains the selected shape, commit hash, run ID, benchmark-derived figures, and limitations; required team/member reports and research card are present.
- **SC-007**: If bonus is pursued, the selected shape meets the must-pass rules and hidden pass rate `>= 0.80`, baseline tests remain green, and bonus evidence is present.

## Assumptions

- The README, assignment documentation, and rubric are the source of truth; the M- and O-identifiers in this specification preserve the IDs from the previously prepared repository requirement matrix, not IDs printed in source documents.
- Work is limited to the existing assignment and the explicitly required deliverables; no additional product capability or technology is introduced.
- Public tests and existing host/runtime support are intended to be reused; the three student shapes remain the team's implementation responsibility.
- The chosen architecture is intentionally undecided until the required measurements are available.
- Optional capabilities remain out of scope unless the team explicitly selects them; optional selection does not make them mandatory.
- The README and rubric both state the selected-shape hidden threshold as `0.75`; the higher `0.80` threshold applies only to bonus eligibility.

## Dependencies

- Each student shape depends on the shared result, trace, policy/tool, approval, and host refund contracts documented in `docs/contracts.md` and `docs/business_rules.md`.
- Orchestrator additionally depends on the existing sanitized handoff and read-only investigator boundary.
- Benchmark, architecture decision, and submission evidence depend on completed shape implementations and generated reports.
- Bonus depends on completion of required work and its stated test/must-pass/hidden-grade thresholds.

## Out of Scope

- Changing the assignment's business rules, rubric, grading thresholds, protected measurement/host/config/data files, or submission format.
- Introducing additional features, product behavior, or technology not required by repository source documents.
- Committing instructor-only hidden grading material, secrets, traces, SQLite files, or manually edited generated reports.
