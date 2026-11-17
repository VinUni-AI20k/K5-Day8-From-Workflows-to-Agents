"""Orchestrator integration: typed delegation and central settlement."""
from lab8.handoff import FACT_KEYS, READONLY_TOOLS
from lab8.shapes import orchestrator


def test_delegated_context_has_allowlisted_facts_and_tools(public_db, monkeypatch):
    original, seen = orchestrator.run_readonly_investigators, []

    def inspect(conn, budget, handoff, principal):
        assert handoff["contract_version"] == "handoff.v1"
        assert set(handoff["facts"]) <= FACT_KEYS
        assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
        assert "parent_secret" not in str(handoff) and "raw_headers" not in str(handoff)
        seen.append(handoff)
        return original(conn, budget, handoff, principal)

    monkeypatch.setattr(orchestrator, "run_readonly_investigators", inspect)
    result = orchestrator.run_claim("C-014", seed=55, store_path=str(public_db))
    assert len(seen) == 1
    assert result.proposal_amount == 150000
    assert result.refund_effects[0]["amount_vnd"] == 120000
