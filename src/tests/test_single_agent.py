from lab8.db import init_store
from lab8.shapes import single
from tests.conftest import CLAIMS, WORLD


def test_single_step_cap_stops_before_refund(tmp_path, monkeypatch):
    store = tmp_path / "single-step-cap.sqlite"
    conn = init_store(store, WORLD, CLAIMS)
    conn.close()
    run_react = single.run_react

    def run_with_one_step(conn, budget, *, observation, decide, max_steps, worker):
        assert max_steps == 8
        return run_react(
            conn, budget, observation=observation, decide=decide, max_steps=1, worker=worker
        )

    def unexpected_refund(*args, **kwargs):
        raise AssertionError("An unfinished ReAct loop must not issue a refund")

    monkeypatch.setattr(single, "run_react", run_with_one_step)
    monkeypatch.setattr(single, "issue_refund", unexpected_refund)

    result = single.run_claim("C-001", seed=11, store_path=str(store))

    assert result.status == "failed"
    assert result.error_reason == "step_cap"
    assert result.proposal_amount == 0
