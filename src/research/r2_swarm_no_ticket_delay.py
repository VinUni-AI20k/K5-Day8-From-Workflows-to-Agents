"""R2 ablation: swarm reference with the ticket-delay channel switched off.

Single changed variable: the swarm may no longer read a delay number from the ticket text,
so `delay_days` always comes from the order row. Everything else is the unchanged
reference swarm: same MockLLM calls (the "parse" call still runs, so cost is identical),
same tools, handoff, host, prices and evaluator.

Run next to the original swarm (from src/):

    python -m lab8.benchmark --shapes swarm,swarm_no_ticket_delay \
        --extra-shape swarm_no_ticket_delay=research.r2_swarm_no_ticket_delay:run_claim \
        --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/r2_ablation.json
"""

from __future__ import annotations

from unittest import mock

from lab8.schemas import RunResult
from lab8.shapes import swarm_reference


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    # The swarm's REFERENCE_WEAKNESS only fires when it parsed a delay from the ticket.
    with mock.patch.object(swarm_reference, "parse_delay_days", lambda _ticket: None):
        return swarm_reference.run_claim(claim_id, seed=seed, store_path=store_path, crash_at=crash_at)
