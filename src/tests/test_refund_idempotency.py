from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund, issue_refund


def test_retry_same_amount_is_one_row(public_db):
    conn = connect(public_db)
    first = issue_refund(conn, "C-001", 35000)
    second = issue_refund(conn, "C-001", 35000)
    effect = get_refund(conn, "C-001")
    audits = committed_audit_count(conn, "C-001")
    conn.close()
    assert first["reason"] == "committed"
    assert second["reason"] == "idempotent_replay"
    assert int(effect["amount_vnd"]) == 35000
    assert effect["idempotency_key"] == "refund:C-001"
    assert audits == 1


def test_retry_different_amount_conflicts_and_keeps_committed(public_db):
    conn = connect(public_db)
    issue_refund(conn, "C-001", 35000)
    second = issue_refund(conn, "C-001", 10000)
    effect = get_refund(conn, "C-001")
    conn.close()
    assert second["conflict"] is True
    assert int(effect["amount_vnd"]) == 35000


def test_crash_after_effect_before_checkpoint_resumes_once(public_db):
    conn = connect(public_db)
    try:
        issue_refund(conn, "C-011", 35000, crash_at="after_effect_before_checkpoint")
        raised = False
    except InjectedCrash:
        raised = True
    assert raised
    assert get_refund(conn, "C-011") is not None
    missing_checkpoint = conn.execute(
        "SELECT 1 FROM checkpoints WHERE claim_id = 'C-011'"
    ).fetchone()
    assert missing_checkpoint is None
    replay = issue_refund(conn, "C-011", 35000)
    count = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'").fetchone()["n"]
    conn.close()
    assert replay["reason"] == "idempotent_replay"
    assert count == 1
    assert committed_audit_count_safe(public_db) == 1


def committed_audit_count_safe(store) -> int:
    conn = connect(store)
    try:
        return committed_audit_count(conn, "C-011")
    finally:
        conn.close()


def test_client_retry_after_unacknowledged_checkpoint_crash_replays_safely(public_db):
    """
    Kịch bản: Server đã ghi tiền vào ledger và checkpoint xong xuôi, nhưng bị crash
    ngay trước khi gửi phản hồi về cho client (crash_at='after_checkpoint').
    Client không nhận được tín hiệu nên gửi tiếp yêu cầu retry.
    Hệ thống phải nhận diện idempotent_replay, giữ nguyên đúng 1 dòng ledger và 1 audit.
    """
    conn = connect(public_db)
    claim_id = "C-011"
    amount = 35000

    # Lần 1: Xử lý thành công trong DB nhưng crash ngay trước khi return phản hồi
    crashed = False
    try:
        issue_refund(conn, claim_id, amount, crash_at="after_checkpoint")
    except InjectedCrash:
        crashed = True
    assert crashed is True, "Phải giả lập được lỗi mất kết nối trước khi phản hồi"

    # Kiểm tra: Trong DB thực chất đã ghi nhận effect và checkpoint rồi
    assert get_refund(conn, claim_id) is not None
    checkpoint = conn.execute("SELECT 1 FROM checkpoints WHERE claim_id = ?", (claim_id,)).fetchone()
    assert checkpoint is not None

    # Lần 2: Client không nhận được phản hồi nên gửi lại yêu cầu retry
    retry_attempt = issue_refund(conn, claim_id, amount)

    # Server phải nhận diện đây là replay an toàn, không ghi tiền đúp
    assert retry_attempt["ok"] is True
    assert retry_attempt["reason"] == "idempotent_replay"
    assert retry_attempt["conflict"] is False

    # Xác thực sổ cái và kiểm toán chỉ có đúng 1 dòng
    count = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?", (claim_id,)).fetchone()["n"]
    assert count == 1
    assert committed_audit_count(conn, claim_id) == 1
    conn.close()

