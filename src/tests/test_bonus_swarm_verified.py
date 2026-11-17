"""Tests for Bonus Topic B3: swarm_verified shape."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bonus.swarm_verified import run_claim as run_swarm_verified
from lab8.db import connect, init_store
from lab8.shapes.swarm_reference import run_claim as run_swarm_reference
from lab8.config_loader import repo_path


@pytest.fixture
def test_env(tmp_path: Path):
    world_path = repo_path("data", "public_world_state.json")
    claims_path = repo_path("data", "public_claims.jsonl")
    world = json.loads(world_path.read_text(encoding="utf-8"))
    claims = [json.loads(line) for line in claims_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    store_path = tmp_path / "test_store.sqlite"
    init_store(store_path, world, claims).close()
    return store_path


def test_verifier_overrides_swarm_hallucination(test_env: Path):
    """At seed 55 on C-002, ticket claims 5 days delay, but DB order O-202 has delay_days=2.

    The unverified swarm hallucinates and approves an illegal refund (20,000 VND).
    swarm_verified must detect the discrepancy, trigger verifier_override, and deny the claim.
    """
    # 1. Unverified swarm wrongly approves refund
    unverified_res = run_swarm_reference("C-002", seed=55, store_path=str(test_env))
    assert unverified_res.status == "resolved"
    assert unverified_res.proposal_amount == 20000

    # 2. swarm_verified detects mismatch and denies
    verified_res = run_swarm_verified("C-002", seed=55, store_path=str(test_env))
    assert verified_res.status == "denied"
    assert verified_res.proposal_amount == 0

    # 3. Verify that 'verifier_override' event was explicitly written to trace
    trace_file = Path(verified_res.trace_path)
    assert trace_file.exists()
    trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
    trace_events = trace_data.get("events", [])
    override_events = [evt for evt in trace_events if evt.get("kind") == "verifier_override"]
    assert len(override_events) == 1
    override_payload = override_events[0]["payload"]
    assert "delay_days" in override_payload["mismatches"]
    assert override_payload["mismatches"]["delay_days"]["expected"] == 2
    assert override_payload["mismatches"]["delay_days"]["actual"] == 5


def test_verifier_preserves_legitimate_claim(test_env: Path):
    """On C-001, order O-107 legitimately has delay_days=4 (>= 3).

    swarm_verified must process without unnecessary override and approve 35,000 VND.
    """
    res = run_swarm_verified("C-001", seed=11, store_path=str(test_env))
    assert res.status == "resolved"
    assert res.proposal_amount == 35000

    trace_file = Path(res.trace_path)
    trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
    trace_events = trace_data.get("events", [])
    override_events = [evt for evt in trace_events if evt.get("kind") == "verifier_override"]
    # No override needed for legitimate match
    assert len(override_events) == 0


def test_verifier_on_adversarial_understated_delay(tmp_path: Path):
    """On an adversarial case where customer understates delay in ticket (C-ADV-02),

    ticket says 'trễ 1 ngày', but DB order has delay_days=4.
    Swarm at seed 55 wrongly denies, but swarm_verified overrides and quotes full entitlement.
    """
    world_path = repo_path("bonus", "world.json")
    claims_path = repo_path("bonus", "cases.jsonl")
    world = json.loads(world_path.read_text(encoding="utf-8"))
    claims = [json.loads(line) for line in claims_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    store_path = tmp_path / "adv_store.sqlite"
    init_store(store_path, world, claims).close()

    verified_res = run_swarm_verified("C-ADV-02", seed=55, store_path=str(store_path))
    assert verified_res.status == "resolved"
    assert verified_res.proposal_amount == 35000
