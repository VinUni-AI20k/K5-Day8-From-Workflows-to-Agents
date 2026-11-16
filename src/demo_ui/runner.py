"""Isolated real-code demo worker. JSON in/out; each subprocess owns its traces."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

from lab8.config_loader import repo_path
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import trial_pass
from lab8.shapes import SHAPES
from bonus.swarm_verified import run_claim as verified

DATASETS = {
    "public": ("data/public_claims.jsonl", "data/public_world_state.json"),
    "bonus": ("bonus/cases.jsonl", "bonus/world.json"),
}
RUNNERS = {**SHAPES, "swarm_verified": verified}
CRASH_POINTS = {"before_effect", "after_effect_before_checkpoint", "after_checkpoint"}


def dataset(name: str) -> tuple[list[dict], dict]:
    if not isinstance(name, str) or name not in DATASETS:
        raise ValueError("Bộ dữ liệu không hợp lệ.")
    cases_path, world_path = DATASETS[name]
    return load_jsonl(repo_path(cases_path)), load_json(repo_path(world_path))


def validate(request: dict) -> dict:
    if not isinstance(request, dict):
        raise ValueError("Yêu cầu phải là một object JSON.")
    cases, _ = dataset(request.get("dataset", "public"))
    if not isinstance(request.get("claim_id"), str) or request["claim_id"] not in {row["claim_id"] for row in cases}:
        raise ValueError("Claim không nằm trong bộ dữ liệu demo.")
    shapes = request.get("shapes")
    if not isinstance(shapes, list) or not shapes or len(shapes) > 4:
        raise ValueError("Chọn từ một đến bốn kiến trúc.")
    if any(not isinstance(s, str) or s not in RUNNERS for s in shapes) or len(set(shapes)) != len(shapes):
        raise ValueError("Kiến trúc không hợp lệ.")
    if type(request.get("seed")) is not int or request["seed"] not in (11, 22, 33, 44, 55):
        raise ValueError("Chọn seed 11, 22, 33, 44 hoặc 55.")
    if request.get("mode", "fresh") not in ("fresh", "retry", "crash"):
        raise ValueError("Kịch bản không hợp lệ.")
    point = request.get("crash_at", "after_effect_before_checkpoint")
    if not isinstance(point, str) or point not in CRASH_POINTS:
        raise ValueError("Vị trí crash không hợp lệ.")
    return request


def snapshot(store: Path, claim_id: str) -> dict:
    conn = connect(store)
    try:
        effect = get_refund(conn, claim_id)
        audit_count = committed_audit_count(conn, claim_id)
        denied = conn.execute(
            "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
            (claim_id,),
        ).fetchall()
        return {
            "refund_count": int(effect is not None),
            "refund_amount": int(effect["amount_vnd"]) if effect else 0,
            "committed_audit_count": audit_count,
            "policy_denied": [json.loads(row["details_json"]).get("reason") for row in denied],
            "effect": effect,
        }
    finally:
        conn.close()


def execute(request: dict) -> dict:
    validate(request)
    cases, world = dataset(request.get("dataset", "public"))
    claim_id, seed = request["claim_id"], request["seed"]
    expected = next(row["expected"] for row in cases if row["claim_id"] == claim_id)
    results = []
    mode = request.get("mode", "fresh")
    for shape in request["shapes"]:
        store = Path(f"{shape}.sqlite")
        init_store(store, world, cases).close()
        attempts = []
        crashed = False

        def call(phase: str, crash_at: str | None = None):
            started = time.time()
            result = RUNNERS[shape](claim_id, seed=seed, store_path=str(store), crash_at=crash_at)
            attempts.append({"phase": phase, "status": result.status, **snapshot(store, claim_id)})
            return result, started

        if mode == "crash":
            point = request.get("crash_at", "after_effect_before_checkpoint")
            try:
                call("crash_requested", point)
            except InjectedCrash:
                crashed = True
                attempts.append({"phase": "crashed", "status": "interrupted", "crash_at": point, **snapshot(store, claim_id)})
            result, started = call("resume")
            result, started = call("retry")
        elif mode == "retry":
            call("first")
            result, started = call("retry")
        else:
            result, started = call("first")
        conn = connect(store)
        try:
            passed, reason = trial_pass(result.as_dict(), expected, conn, started_at=started)
        finally:
            conn.close()
        payload = result.as_dict()
        trace = load_json(payload.pop("trace_path"))
        results.append({
            **payload, "passed": passed, "validation_reason": reason,
            "trace": trace, "ledger": snapshot(store, claim_id),
            "attempts": attempts, "crash_observed": crashed,
        })
    return {"claim_id": claim_id, "seed": seed, "mode": mode, "results": results}


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(execute(json.load(sys.stdin)), ensure_ascii=False))
