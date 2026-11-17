"""One bounded repair, using a fresh principal-scoped structured order."""
from lab8.runtime import dispatch

FACTS = ("delay_days", "status", "damage_verified")


def verify_order(conn, budget, trace, *, candidate, quote_payload, order_id, principal_id):
    view = dispatch(conn, budget, "lookup_order", {
        "order_id": order_id, "principal_id": principal_id}, worker=True)
    if not view.get("visible"):
        # No write may be based on an order that ceased to be visible.
        trace.add("verifier_rejected", {"reason": view.get("reason")})
        return {}, {"amount_vnd": 0, "reason": "verifier_order_not_visible"}
    trusted = view["order"]
    changed = [key for key in FACTS if candidate.get(key) != trusted.get(key)]
    trace.add("verifier_check", {"fields": list(FACTS), "matched": not changed})
    if not changed:
        return candidate, quote_payload
    corrected = dispatch(conn, budget, "compute_compensation", {"order": trusted}, worker=True)
    trace.add("verifier_override", {
        "fields": changed, "before": {key: candidate.get(key) for key in FACTS},
        "after": {key: trusted.get(key) for key in FACTS},
        "proposal_before": quote_payload["amount_vnd"],
        "proposal_after": corrected["amount_vnd"], "repair_round": 1,
    })
    return trusted, corrected
