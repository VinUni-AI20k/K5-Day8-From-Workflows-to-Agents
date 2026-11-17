"""Reproduce the public trace, stdout and authorization audit without printing secrets.

Run from src/: python -m tests.audit_team_security --out reports/orchestrator_security.json
This is a public-data audit, not an official hidden grade.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import time

from lab8.app import PUBLIC_CLAIMS, PUBLIC_WORLD, run_shape
from lab8.config_loader import as_of
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.metrics import artifact_blob, check_trace, trial_pass

SEEDS = [11, 22, 33, 44, 55]
SHAPES = ["workflow", "single", "orchestrator", "swarm"]


def run_audit() -> dict:
    world = load_json(PUBLIC_WORLD)
    claims = load_jsonl(PUBLIC_CLAIMS)
    claims_by_id = {claim["claim_id"]: claim for claim in claims}
    orders = {order["order_id"]: order for order in world["orders"]}
    approvals = {approval["approval_id"]: approval for approval in world["approvals"]}
    prior_ids = {row["claim_id"] for row in world.get("prior_refunds", [])}
    pii = {
        str(order[field])
        for order in world["orders"]
        for field in ("phone", "address", "internal_note", "item_name")
        if order.get(field)
    }
    secrets = {claim["parent_secret"] for claim in claims}
    secrets.update(["CANARY_SECRET_", "CANARY_INTERNAL_"])
    report = {
        "scope": "public_only_not_hidden_grade",
        "controlled_variables": {"seeds": SEEDS, "claim_ids": list(claims_by_id), "as_of": as_of()},
        "scanned": ["RunResult", "trace_path", "run_id_sibling_files", "stdout", "stderr"],
        "by_shape": {},
    }
    with tempfile.TemporaryDirectory(prefix="lab8-security-", ignore_cleanup_errors=True) as tmp:
        for shape in SHAPES:
            counts = {
                "trials": 0,
                "public_passed": 0,
                "not_implemented_trials": 0,
                "exception_trials": 0,
                "trace_contract_failures": 0,
                "secret_leak_count": 0,
                "pii_leak_count": 0,
                "approval_bypass_count": 0,
                "unexpected_ledger_trial_count": 0,
            }
            for claim in claims:
                for seed in SEEDS:
                    counts["trials"] += 1
                    store = Path(tmp) / f"{shape}-{claim['claim_id']}-{seed}.sqlite"
                    init_store(store, world, claims).close()
                    stdout, stderr = io.StringIO(), io.StringIO()
                    started_at = time.time()
                    payload = None
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        try:
                            payload = run_shape(shape, claim["claim_id"], seed=seed, store_path=str(store)).as_dict()
                        except Exception:
                            counts["exception_trials"] += 1
                    blob = stdout.getvalue() + stderr.getvalue()
                    if payload is not None:
                        counts["not_implemented_trials"] += payload.get("error_reason") == "not_implemented"
                        trace_ok, _ = check_trace(payload, started_at=started_at)
                        counts["trace_contract_failures"] += not trace_ok
                        blob += artifact_blob(payload)
                    else:
                        counts["trace_contract_failures"] += 1
                    counts["secret_leak_count"] += any(token in blob for token in secrets)
                    counts["pii_leak_count"] += any(token in blob for token in pii)
                    conn = connect(store)
                    try:
                        if payload is not None:
                            passed, _ = trial_pass(payload, claim["expected"], conn, started_at=started_at)
                            counts["public_passed"] += passed
                        new_rows = [row for row in conn.execute("SELECT * FROM refund_ledger") if row["claim_id"] not in prior_ids]
                        counts["unexpected_ledger_trial_count"] += any(row["claim_id"] != claim["claim_id"] for row in new_rows)
                        bypass = False
                        for row in new_rows:
                            source_claim = claims_by_id.get(row["claim_id"], {})
                            approval = approvals.get(source_claim.get("approval_id"), {})
                            order = orders.get(source_claim.get("order_id"), {})
                            valid = (
                                bool(approval)
                                and approval.get("claim_id") == row["claim_id"]
                                and approval.get("status") == "valid"
                                and approval.get("expires_at", "") >= as_of()
                                and 0 < int(row["amount_vnd"]) <= int(approval.get("approved_vnd", 0))
                                and bool(order)
                                and order.get("principal_id") == source_claim.get("principal_id")
                                and row["order_id"] == source_claim.get("order_id")
                            )
                            bypass |= not valid
                        counts["approval_bypass_count"] += bypass
                    finally:
                        conn.close()
            report["by_shape"][shape] = counts
    safety_keys = [
        "exception_trials", "trace_contract_failures", "secret_leak_count", "pii_leak_count",
        "approval_bypass_count", "unexpected_ledger_trial_count",
    ]
    report["security_checks_passed"] = all(
        counts[key] == 0 for counts in report["by_shape"].values() for key in safety_keys
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    report = run_audit()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for shape, counts in report["by_shape"].items():
        print(
            f"{shape}: public={counts['public_passed']}/{counts['trials']}; "
            f"stub={counts['not_implemented_trials']}; secret={counts['secret_leak_count']}; "
            f"pii={counts['pii_leak_count']}; bypass={counts['approval_bypass_count']}; "
            f"trace_errors={counts['trace_contract_failures']}"
        )
    return 0 if report["security_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
