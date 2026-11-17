# Research: Claim Shape Implementation

## Scope and Findings

The repository already defines the implementation architecture, runtime versions, test harness,
shared data contracts, host boundaries, and grading workflow. No new technology selection is
required. The research phase therefore records repository-derived decisions; no external
technology research or speculative alternative is needed.

### Decision: Reuse the existing Python `lab8` package

- **Decision**: Implement only the three assigned shape modules under `src/lab8/shapes/` and
  reuse current package helpers.
- **Rationale**: The README and source map identify these as the student-owned files; helper
  modules already provide the host, MockLLM, tool, trace, and result behavior.
- **Alternatives considered**: New package/service or new framework. Rejected because neither is
  required by the assignment and both would expand scope and break comparison conditions.

### Decision: Keep shared contracts and host modules unchanged

- **Decision**: Treat `schemas.py`, `shapes.common.py`, `tools.py`, `compensation.py`,
  `durability.py`, `policy.py`, `runtime.py`, `handoff.py`, and `trace.py` as interfaces and
  existing infrastructure, not parallel implementation targets.
- **Rationale**: The docs define these boundaries; assignment rules explicitly protect host,
  policy, metric, config, and data sources. `shapes.common.finish()` already derives ledger fields
  and writes trace output consistently.
- **Alternatives considered**: Rework host or create another abstraction layer. Rejected because
  existing code meets the documented role and changes are restricted or unnecessary.

### Decision: Parallelize only isolated shape implementations after a contract gate

- **Decision**: Give each shape module one owner and have contributors add tests in distinct
  test files after shared callable/result/refund/trace contracts are agreed.
- **Rationale**: The shapes share the same evaluator interface but have distinct internal
  approaches. This supports independent work without simultaneous edits to shared modules.
- **Alternatives considered**: Multiple contributors editing common helpers or the public student
  matrix. Rejected because that creates merge contention and risks weakening the grader contract.

### Decision: Use repository-defined tests, reports, and thresholds

- **Decision**: Validate with pytest, the student matrix, the crash suite, the required benchmark,
  and the submission checker; report generated evidence without changing JSON by hand.
- **Rationale**: These commands, datasets, seeds, and acceptance thresholds are specified in the
  README, rubric, source README, and report instructions.
- **Alternatives considered**: New performance target or substitute benchmark. Rejected because
  no such target is defined and it would change the source criteria.

## Resolved Technical Context

- Python 3.11–3.13; pytest 8.x; PyYAML 6.x (`src/requirements.txt`).
- SQLite world/ledger; each independent run uses its own store except explicit retry/resume tests.
- Windows, macOS, and Linux are supported targets.
- MockLLM is seeded and offline; its simulated cost is not a real API bill and latency is not
  measured.
- Required public comparison: four shapes, at least 10 public claims, seeds `11,22,33,44,55`.
- Selected-shape hidden acceptance is `>= 0.75`; bonus eligibility requires `>= 0.80`.

## Unresolved Questions

None for technical design. The group member roster is not in the spec input; concrete named task
owners must be assigned in `/speckit.tasks` before implementation, as required by the constitution.
