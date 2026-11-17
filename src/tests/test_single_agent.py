"""Single-agent integration: actual bounded runtime, charged model, no write action."""
from lab8.shapes import single


def test_single_uses_runtime_and_only_read_actions(public_db, monkeypatch):
    original, observed = single.run_react, []

    def bounded(conn, budget, **kwargs):
        assert kwargs["max_steps"] == 8
        decide = kwargs["decide"]

        def record(observation):
            action = decide(observation)
            observed.append(action.get("tool", "final"))
            return action

        kwargs["decide"] = record
        return original(conn, budget, **kwargs)

    monkeypatch.setattr(single, "run_react", bounded)
    result = single.run_claim("C-001", seed=11, store_path=str(public_db))
    assert observed == ["lookup_order", "compute_compensation", "final"]
    assert result.model_calls == len(observed) <= 8
    assert result.status == "resolved" and result.cost_estimate > 0
