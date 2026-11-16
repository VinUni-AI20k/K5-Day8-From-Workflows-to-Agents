from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
import yaml


def _src_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def test_environment_and_runtime_compliance():
    """Verify runtime environment meets Lab 8 specifications (Python 3.11-3.13, SQLite)."""
    assert (3, 11) <= sys.version_info[:2] <= (3, 13), f"Python version {sys.version} not in 3.11-3.13"
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("SELECT sqlite_version()")
    ver = cursor.fetchone()[0]
    assert ver is not None, "SQLite is not accessible"
    conn.close()


def test_fixtures_integrity():
    """Verify that public claims and world state fixtures are complete and valid."""
    data_dir = _src_dir() / "data"
    claims_file = data_dir / "public_claims.jsonl"
    world_file = data_dir / "public_world_state.json"

    assert claims_file.is_file(), "data/public_claims.jsonl missing"
    assert world_file.is_file(), "data/public_world_state.json missing"

    claims = []
    with open(claims_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                claims.append(json.loads(line))

    assert len(claims) == 14, f"Expected 14 public claims, got {len(claims)}"
    claim_ids = {c["claim_id"] for c in claims}
    for i in range(1, 15):
        assert f"C-{i:03d}" in claim_ids, f"C-{i:03d} missing from public claims"

    with open(world_file, encoding="utf-8") as f:
        world = json.load(f)
    assert "orders" in world
    assert "policies" in world
    assert "approvals" in world


def test_config_manifests_validity():
    """Verify that configuration manifests are syntactically valid YAML."""
    config_dir = _src_dir() / "config"
    for filename in ("autonomy_policy.yaml", "pricing.yaml", "tools.manifest.v1.1.yaml"):
        filepath = config_dir / filename
        assert filepath.is_file(), f"Config file {filename} missing"
        with open(filepath, encoding="utf-8") as f:
            content = yaml.safe_load(f)
            assert content is not None, f"Config file {filename} is empty or invalid YAML"


def test_crash_report_safety_status():
    """Verify that reports/crash.json exists and meets the 20/20 must-pass gate."""
    crash_file = _src_dir() / "reports" / "crash.json"
    assert crash_file.is_file(), "reports/crash.json missing"
    with open(crash_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("crash_safety") == "20/20", f"crash_safety is {data.get('crash_safety')}, expected 20/20"
