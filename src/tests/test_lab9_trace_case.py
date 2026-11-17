"""Regression test for trace_case C-002@11 (FM-03: ticket_trust)."""

import pytest

pytestmark = pytest.mark.student


def _eval_db_fact(shape: str) -> bool:
    # Lazy import so Lab 8 CI (without requirements-lab9.txt) can still collect tests.
    from pydantic_evals.evaluators import EvaluatorContext
    from lab9 import graders, trace_case

    case = trace_case.investigate(shape, "C-002", 11)
    ctx = EvaluatorContext(
        name="C-002@11",
        inputs={"claim_id": "C-002", "seed": 11},
        metadata=None,
        expected_output=case["label"],
        output=case["trial"],
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )
    return bool(graders.DbFactKept().evaluate(ctx).value) and bool(case["trial"]["lab8_pass"])


def test_c002_seed11_fixed_passes_and_seeded_regression_fails():
    assert _eval_db_fact("fixed") is True
    assert _eval_db_fact("seeded_regression") is False
