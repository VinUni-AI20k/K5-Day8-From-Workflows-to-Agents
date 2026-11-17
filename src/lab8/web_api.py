"""HTTP API for the Claim Flow Studio frontend.

Uses only the stdlib so lab deps stay lean.

    python -m lab8.web_api
    # http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import tempfile
import traceback
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from lab8.app import PUBLIC_CLAIMS, prepare_store, run_shape
from lab8.config_loader import repo_path
from lab8.db import load_jsonl
from lab8.durability import InjectedCrash
from lab8.shapes import SHAPES

HOST = "127.0.0.1"
PORT = 8765


def _sanitize_claim(raw: dict[str, Any]) -> dict[str, Any]:
    expected = raw.get("expected") or {}
    return {
        "claim_id": raw["claim_id"],
        "principal_id": raw.get("principal_id"),
        "order_id": raw.get("order_id"),
        "ticket": raw.get("ticket"),
        "approval_id": raw.get("approval_id"),
        "matrix_id": raw.get("matrix_id"),
        "expected": {
            "status": expected.get("status"),
            "proposal_amount": expected.get("proposal_amount", 0),
            "refund_vnd": expected.get("refund_vnd", 0),
            "refund_count": expected.get("refund_count", 0),
            "audit_refund_committed": expected.get("audit_refund_committed", 0),
            "policy_denied": bool(expected.get("policy_denied")),
            "approval_ok": bool(expected.get("approval_ok")),
        },
    }


def _load_claims() -> list[dict[str, Any]]:
    return [_sanitize_claim(row) for row in load_jsonl(PUBLIC_CLAIMS)]


def _read_trace(trace_path: str | None) -> dict[str, Any]:
    if not trace_path:
        return {"run_id": None, "steps": 0, "events": []}
    path = Path(trace_path)
    if not path.is_file():
        # Trace may be relative to src/ cwd depending on how the process started.
        alt = repo_path(trace_path)
        path = alt if alt.is_file() else Path.cwd() / trace_path
    if not path.is_file():
        return {"run_id": None, "steps": 0, "events": [], "missing": True, "path": trace_path}
    return json.loads(path.read_text(encoding="utf-8"))


def _run_live(payload: dict[str, Any]) -> dict[str, Any]:
    shape = payload.get("shape")
    claim_id = payload.get("claim_id")
    seed = payload.get("seed")
    crash_at = payload.get("crash_at")

    if shape not in SHAPES:
        raise ValueError(f"unknown shape {shape!r}; choose from {', '.join(SHAPES)}")
    if not isinstance(claim_id, str) or not claim_id:
        raise ValueError("claim_id is required")
    if not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    claims = {c["claim_id"]: c for c in _load_claims()}
    claim = claims.get(claim_id)
    if claim is None:
        raise ValueError(f"unknown claim_id {claim_id!r}")

    tmp = Path(tempfile.gettempdir()) / f"lab8-web-{uuid.uuid4().hex}.sqlite"
    prepare_store(tmp)
    try:
        result = run_shape(
            shape,
            claim_id,
            seed=seed,
            store_path=str(tmp),
            crash_at=crash_at,
        )
        result_dict = result.as_dict()
        crashed = False
        crash_point = None
    except InjectedCrash as exc:
        result_dict = None
        crashed = True
        crash_point = str(exc)

    trace = _read_trace(None if result_dict is None else result_dict.get("trace_path"))
    # If crash happened after trace.write(), try to find the expected run id file.
    if crashed and (not trace.get("events")):
        from lab8.schemas import make_run_id

        guess = repo_path("traces", f"{make_run_id(shape, claim_id, seed)}.json")
        if guess.is_file():
            trace = json.loads(guess.read_text(encoding="utf-8"))

    refund_vnd = 0
    if result_dict:
        for effect in result_dict.get("refund_effects") or []:
            refund_vnd += int(effect.get("amount_vnd") or 0)

    return {
        "ok": not crashed,
        "crashed": crashed,
        "crash_at": crash_point,
        "shape": shape,
        "seed": seed,
        "claim": claim,
        "result": result_dict,
        "trace": trace,
        "refund_vnd": refund_vnd,
        "store_path": str(tmp),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "Lab8WebAPI/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[web_api] {self.address_string()} - {fmt % args}")

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status: int, body: dict[str, Any] | list[Any]) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/api/health", "/health"):
            self._json(200, {"ok": True, "service": "lab8-web-api"})
            return
        if path == "/api/shapes":
            self._json(
                200,
                {
                    "shapes": list(SHAPES.keys()),
                    "seeds": [11, 22, 33, 44, 55],
                },
            )
            return
        if path == "/api/claims":
            self._json(200, {"claims": _load_claims()})
            return
        self._json(404, {"error": "not_found", "path": path})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid_json"})
            return

        if path != "/api/run":
            self._json(404, {"error": "not_found", "path": path})
            return

        try:
            body = _run_live(payload if isinstance(payload, dict) else {})
            self._json(200, body)
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:  # noqa: BLE001 - surface to the studio UI
            self._json(
                500,
                {
                    "error": str(exc),
                    "traceback": traceback.format_exc(limit=8),
                },
            )


def main() -> int:
    import os

    # Trace() writes relative to cwd; pin cwd to src/ so paths stay stable.
    os.chdir(repo_path())
    traces = Path("traces")
    traces.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Lab8 web API listening on http://{HOST}:{PORT}")
    print("Endpoints: GET /api/health /api/claims /api/shapes  POST /api/run")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
