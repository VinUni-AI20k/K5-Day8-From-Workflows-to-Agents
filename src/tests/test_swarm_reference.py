import pytest

from lab8.db import connect
from lab8.metrics import trial_pass
from lab8.shapes.swarm_reference import run_claim
from tests.conftest import BY_ID


@pytest.mark.parametrize(
    "claim_id",
    ["C-001", "C-002", "C-003", "C-004", "C-005", "C-006", "C-007", "C-008", "C-009", "C-010", "C-013", "C-014"],
)
def test_reference_swarm_passes_published_traps(public_db, claim_id):
    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn)
    finally:
        conn.close()
    assert passed, reason


def test_reference_weakness_is_visible_on_public_t02(tmp_path):
    """Seed 55 trusts the ticket (5 days) over the order row (2 days) and pays.

    This keeps the variance the lab asks students to measure visible on the public set.
    """
    from lab8.db import init_store
    from tests.conftest import CLAIMS, WORLD

    outcomes = {}
    for seed in (11, 55):
        store = tmp_path / f"t02-{seed}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        result = run_claim("C-002", seed=seed, store_path=str(store))
        conn = connect(store)
        try:
            outcomes[seed] = trial_pass(result.as_dict(), BY_ID["C-002"]["expected"], conn)[0]
        finally:
            conn.close()
    assert outcomes == {11: True, 55: False}


def test_swarm_seed_divisible_by_5_overrides_delay_with_ticket(tmp_path):
    """Kiểm tra khi seed chia hết cho 5 (ví dụ seed 55), swarm tin ticket và ghi nhận sự kiện model_override trong trace."""
    import json
    from pathlib import Path
    from lab8.db import init_store
    from tests.conftest import CLAIMS, WORLD

    store = tmp_path / "t02-override.sqlite"
    init_store(store, WORLD, CLAIMS).close()

    # C-002: Trong database order delay_days là 2, nhưng ticket ghi trễ 5 ngày.
    # Với seed=55 (seed % 5 == 0), swarm sẽ kích hoạt REFERENCE_WEAKNESS và ghi event 'model_override'.
    result = run_claim("C-002", seed=55, store_path=str(store))

    # Đọc file trace được ghi ra từ result.trace_path
    trace_data = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    events = [ev["kind"] for ev in trace_data["events"]]
    assert "model_override" in events

    # Kiểm tra payload của sự kiện model_override ghi nhận delay_days = 5 thay vì 2 trong order DB
    override_event = next(ev for ev in trace_data["events"] if ev["kind"] == "model_override")
    assert override_event["payload"]["delay_days"] == 5
