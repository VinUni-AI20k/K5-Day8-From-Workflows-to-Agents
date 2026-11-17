# Quickstart: Plan Validation

All commands run from `src/`. Use the project's documented environment setup in
[`src/README.md`](../../src/README.md) before running them. This guide validates the plan
and later implementation; it does not add implementation code.

## Prerequisites

- Python 3.11–3.13 and dependencies from `requirements.txt` are installed.
- Current working directory is `src/`.
- Begin with the repository's expected clean host gate. Do not change protected host/config/data
  files to make a gate pass.

## Baseline Before Parallel Work

```bash
python -m lab8.smoke
python -m pytest -q
```

Expected: smoke prints `lab8.smoke pass`; host suite passes. The starter README documents the
initial baseline as `52 passed, 248 deselected` before contributors add tests.

## Per-Shape Checks

Run one student subset at a time while implementing; replace the selector for each owner:

```bash
python -m pytest -q -m student -o addopts= -k workflow
python -m pytest -q -m student -o addopts= -k single
python -m pytest -q -m student -o addopts= -k orchestrator
```

Expected: all selected shape trials pass; the selector can match test names/parameters as
configured by pytest. Run the full student matrix after integration:

```bash
python -m pytest -q -m student -o addopts=
python -m pytest -q
```

Expected: required student cases and normal host tests pass. Preserve the reference swarm's
documented expected miss; do not weaken its assertion.

## Crash and Benchmark Evidence

```bash
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

Expected: `crash_safety` is `20/20`; benchmark covers four shapes, five prescribed seeds, and
the required public corpus (at least 10 claims). Reports are tool-generated and must not be
edited manually.

## Submission Gate

After required reports and documents have been completed:

```bash
python -m lab8.check_submission
```

Expected: `0 FAIL`. Official hidden pass rate is graded separately and must be at least `0.75`
for the selected shape. Bonus requires at least `0.80` and all rubric prerequisites.
