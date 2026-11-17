"""R4 ablation: reuse workflow unchanged, disabling only its draft model call.

Run sequentially through lab8.benchmark --extra-shape. The scoped patches modify
module globals and are not intended for concurrent calls in the same process.
This helper supports the mandatory research card, not a bonus submission.
"""

from __future__ import annotations

from unittest.mock import patch

from lab8.schemas import Budget, RunResult
from lab8.shapes import workflow

SHAPE = "workflow_no_draft"


def _skip_draft(budget: Budget, *, seed: int, purpose: str, prompt: str) -> str:
    if purpose != "draft":
        raise ValueError("This ablation may disable only a draft call")
    return ""


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    # Different identity prevents baseline traces from being overwritten. Neither
    # patch changes tools, policy, quote, ledger, or the shared evaluator.
    with patch.object(workflow, "SHAPE", SHAPE), patch.object(workflow, "complete", _skip_draft):
        return workflow.run_claim(claim_id, seed=seed, store_path=store_path, crash_at=crash_at)
