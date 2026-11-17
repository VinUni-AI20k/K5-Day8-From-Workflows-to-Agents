<!--
Sync Impact Report
Version change: none (new constitution) -> 1.0.0
Modified principles: none
Added sections: Core Principles, Scope and Quality Constraints, Development Workflow, Governance
Removed sections: none
Follow-up TODOs: Confirm the original ratification date.
-->
# LogiX-VN Workflows to Agents Constitution

## Core Principles

### I. Repository Sources Define Scope
README, assignment documents, and the rubric are the authoritative sources of project
requirements. Every specification, plan, task, implementation, and verification MUST trace
back to those sources. Work MUST stay within the agreed scope; proposals not present in the
source requirements MUST be labeled as proposals and MUST NOT be implemented without
agreement.

### II. Reuse the Existing Architecture
Contributors MUST inspect and prefer reuse of existing code, interfaces, and architecture
before introducing new modules or patterns. Changes MUST preserve established contracts
unless an approved requirement explicitly calls for changing them. This avoids unnecessary
complexity and keeps the assignment's implementations comparable.

### III. Tasks Have Owners and Verifiable Outcomes
Every task MUST identify one responsible owner, its expected deliverable, and objective
completion criteria. Each task MUST include test evidence or reproducible verification
instructions. A task is not complete until its criteria are met and its evidence is available.

### IV. Agree on Shared Contracts Before Parallel Work
Before parallel implementation begins, contributors MUST agree on the interface or API
contract for every module used by multiple contributors. Implementations and tests MUST
conform to that contract. Contract changes MUST be communicated to affected owners and
reviewed before dependent work proceeds.

### V. Isolated Ownership and Pull Request Review
Each member MUST develop on a Git branch assigned to that member. A contributor MUST NOT
make unapproved changes to a module owned by another member. Every change MUST be submitted
and reviewed through a Pull Request before integration; review MUST check requirement scope,
contract compatibility, and the task's verification evidence.

## Scope and Quality Constraints

- Mandatory assignment requirements MUST be completed before optional bonus work is started.
- Specifications, plans, tasks, implementation, and review MUST follow the same source-of-truth
  and scope rules in this constitution.
- Verification evidence MUST be reproducible from the documented commands or tests; claims of
  completion MUST NOT rely on unverified results.

## Development Workflow

- Before implementation, identify the source requirement and record the task owner, deliverable,
  acceptance criteria, and verification method in the task breakdown.
- Before splitting shared-module work, define and review its interface or API contract.
- Implement assigned work on the owner's branch, then submit a Pull Request with relevant test
  evidence or verification instructions.
- Reviewers MUST verify scope, shared-contract compliance, acceptance criteria, and evidence
  before approving integration.
- Schedule optional bonus tasks only after required tasks meet their completion criteria.

## Governance

- This constitution governs the full Spec-Driven Development lifecycle: specification, planning,
  task definition, implementation, verification, and review. In case of conflict, repository
  requirements remain authoritative for assignment scope and this constitution governs the
  development process.
- Amendments MUST be proposed and reviewed through a Pull Request. The amendment MUST describe
  its rationale and impact on existing specifications, plans, tasks, and work in progress.
- Constitution versions use semantic versioning. MAJOR denotes incompatible governance changes;
  MINOR denotes new or materially expanded principles or sections; PATCH denotes clarifications
  and non-semantic corrections.
- Every Pull Request review MUST check compliance with applicable principles. Task completion
  and project reviews MUST identify any deviations and record their resolution before affected
  work is accepted.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm original adoption date | **Last Amended**: 2026-11-16
