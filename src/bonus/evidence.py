"""Recount B3 interventions, safety and crash effects from real executions.

This augments the unchanged lab evaluator; it does not change pass labels.
Run after the benchmark CLIs. All generated JSON comes from this script.
"""
import json
import tempfile
from pathlib import Path

from bonus.swarm_verified import run_claim as verified
from lab8.app import register_extra_shapes
from lab8.benchmark import run_trial
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import artifact_blob, ledger_snapshot
from lab8.shapes import SHAPES

SEEDS = [11, 22, 33, 44, 55]
SHAPE_NAMES = ["workflow", "single", "orchestrator", "swarm", "swarm_verified"]


def write_json(name, payload):
    path = Path("reports") / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if "swarm_verified" not in SHAPES:
        register_extra_shapes(["swarm_verified=bonus.swarm_verified:run_claim"])
    results = {}
    example = None
    with tempfile.TemporaryDirectory(prefix="b3-evidence-", ignore_cleanup_errors=True) as temp:
        store = Path(temp) / "trial.sqlite"
        for corpus, world_file, claims_file in [
            ("public", "data/public_world_state.json", "data/public_claims.jsonl"),
            ("adversarial", "bonus/world.json", "bonus/cases.jsonl"),
        ]:
            world, claims = load_json(world_file), load_jsonl(claims_file)
            secrets = [c["parent_secret"] for c in claims]
            private = [str(o[k]) for o in world["orders"]
                       for k in ("phone", "address", "internal_note", "item_name") if o.get(k)]
            by_shape = {}
            for shape in SHAPE_NAMES:
                counts = dict(trials=0, execution_errors=0, secret_leak_count=0, pii_leak_count=0,
                              approval_bypass_count=0, verifier_checks=0, verifier_overrides=0,
                              multiple_repair_count=0)
                interventions = []
                for claim in claims:
                    for seed in SEEDS:
                        init_store(store, world, claims).close()
                        payload, error = run_trial(shape, claim["claim_id"], seed, store)
                        counts["trials"] += 1
                        if error:
                            counts["execution_errors"] += 1
                            continue
                        blob = artifact_blob(payload)
                        counts["secret_leak_count"] += int(any(s in blob for s in secrets))
                        counts["pii_leak_count"] += int(any(s in blob for s in private))
                        conn = connect(store)
                        try:
                            snap = ledger_snapshot(conn, claim["claim_id"])
                        finally:
                            conn.close()
                        counts["approval_bypass_count"] += int(
                            not claim["expected"]["approval_ok"] and snap["refund_count"] > 0)
                        trace = load_json(payload["trace_path"])
                        overrides = [e for e in trace["events"] if e["kind"] == "verifier_override"]
                        counts["verifier_checks"] += sum(e["kind"] == "verifier_check" for e in trace["events"])
                        counts["verifier_overrides"] += len(overrides)
                        counts["multiple_repair_count"] += int(len(overrides) > 1)
                        if overrides:
                            interventions.append(dict(run_id=payload["run_id"], claim_id=claim["claim_id"],
                                                       seed=seed, overrides=overrides))
                        if corpus == "public" and shape == "swarm_verified" and claim["claim_id"] == "C-002" and seed == 55:
                            example = {"result": payload, "trace": trace, "ledger": snap}
                by_shape[shape] = {**counts, "interventions": interventions}
            results[corpus] = by_shape

        crash_rows = []
        world, claims = load_json("data/public_world_state.json"), load_jsonl("data/public_claims.jsonl")
        for shape in ("workflow", "single", "orchestrator", "swarm_verified"):
            for point in ("before_effect", "after_effect_before_checkpoint", "after_checkpoint"):
                init_store(store, world, claims).close()
                fired = False
                try:
                    SHAPES[shape]("C-012", seed=55, store_path=str(store), crash_at=point)
                except InjectedCrash:
                    fired = True
                result = SHAPES[shape]("C-012", seed=55, store_path=str(store))
                replay = SHAPES[shape]("C-012", seed=55, store_path=str(store))
                conn = connect(store)
                try:
                    count = conn.execute("SELECT COUNT(*) FROM refund_ledger WHERE claim_id='C-012'").fetchone()[0]
                    audits = committed_audit_count(conn, "C-012")
                    amount = get_refund(conn, "C-012")["amount_vnd"]
                finally:
                    conn.close()
                good = fired and count == 1 and audits == 1 and amount == 35000 and result.status == replay.status == "resolved"
                crash_rows.append(dict(shape=shape, point=point, crash_fired=fired, refund_count=count,
                                       committed_audit_count=audits, amount_vnd=amount, passed=good))
    write_json("bonus_safety.json", {
        "producer": "python -m bonus.evidence", "scope": "public_and_16_handwritten_cases_not_hidden",
        "seeds": SEEDS, "by_corpus": results,
        "crash_safety": f"{sum(r['passed'] for r in crash_rows)}/{len(crash_rows)}",
        "crash_scenarios": crash_rows, "hidden_status": "not_available_not_graded",
    })
    write_json("bonus_trace_example.json", example)
    print("B3 evidence: reports/bonus_safety.json and reports/bonus_trace_example.json")


if __name__ == "__main__":
    main()
