"""Local-only UI server: python -m demo_ui.server --open (no new dependencies)."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from threading import Timer
from urllib.parse import urlsplit
import webbrowser

from demo_ui.runner import dataset, validate
from lab8.config_loader import repo_path
from lab8.mock_llm import parse_delay_days

ASSETS = Path(__file__).parent / "assets"
REPORTS = {
    "benchmark.json", "crash.json", "bonus_public.json", "bonus_adversarial.json",
    "bonus_safety.json", "bonus_verifier_trace.json",
}


def scrub(value):
    """The demo never serves private fixture columns or canary strings."""
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()
                if key not in {"parent_secret", "raw_headers", "raw_headers_json", "phone", "address", "internal_note", "item_name"}}
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r"CANARY_(?:SECRET|INTERNAL)_[\w-]+", "[đã ẩn]", value)
        return re.sub(r"(?<!\d)0\d{9,10}(?!\d)", "[đã ẩn số điện thoại]", value)
    return value


def catalog() -> dict:
    catalogs = {}
    for name in ("public", "bonus"):
        cases, world = dataset(name)
        orders = {row["order_id"]: row for row in world["orders"]}
        rows = []
        for case in cases:
            order = orders.get(case.get("order_id"))
            visible = bool(order and order["principal_id"] == case["principal_id"])
            rows.append({
                "claim_id": case["claim_id"], "matrix_id": case.get("matrix_id"),
                "category": case.get("category"), "ticket": case["ticket"],
                "order_id": case.get("order_id"), "ticket_delay_days": parse_delay_days(case["ticket"]),
                "visible": visible,
                "order": {key: order[key] for key in (
                    "status", "delay_days", "shipping_fee_vnd", "paid_vnd", "damage_verified",
                )} if visible else None,
                "expected": {key: case["expected"][key] for key in (
                    "status", "proposal_amount", "refund_vnd", "refund_count", "approval_ok", "policy_denied",
                )},
                "label_reason": case.get("label_reason"),
            })
        catalogs[name] = rows
    return scrub({"datasets": catalogs, "seeds": [11, 22, 33, 44, 55]})


def reports() -> dict:
    return {name.removesuffix(".json"): json.loads(repo_path("reports", name).read_text(encoding="utf-8"))
            for name in sorted(REPORTS) if repo_path("reports", name).is_file()}


def run_demo(request: dict) -> dict:
    validate(request)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_path()) + os.pathsep + env.get("PYTHONPATH", "")
    # A process per request isolates SQLite and trace paths even with concurrent viewers.
    with tempfile.TemporaryDirectory(prefix="logix-ui-", ignore_cleanup_errors=True) as directory:
        completed = subprocess.run(
            [sys.executable, "-m", "demo_ui.runner"],
            input=json.dumps(request, ensure_ascii=False), text=True, encoding="utf-8",
            capture_output=True, timeout=30, cwd=directory, env=env,
        )
        if completed.returncode != 0:
            raise RuntimeError("Không chạy được claim. Kiểm tra môi trường Python của dự án.")
        return scrub(json.loads(completed.stdout))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send(self, status: int, body: bytes, kind: str):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload):
        self.send(status, json.dumps(scrub(payload), ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/catalog":
            return self.send_json(200, catalog())
        if path == "/api/reports":
            return self.send_json(200, reports())
        if path == "/api/health":
            return self.send_json(200, {"ok": True})
        if path.startswith("/reports/") and path.removeprefix("/reports/") in REPORTS:
            name = path.removeprefix("/reports/")
            file = repo_path("reports", name)
            if file.is_file():
                return self.send(200, file.read_bytes(), "application/json; charset=utf-8")
        files = {"/": ("index.html", "text/html"), "/styles.css": ("styles.css", "text/css"), "/app.js": ("app.js", "text/javascript")}
        if path in files:
            name, mime = files[path]
            return self.send(200, (ASSETS / name).read_bytes(), mime + "; charset=utf-8")
        self.send_json(404, {"error": "Không tìm thấy trang."})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/run":
            return self.send_json(404, {"error": "Không tìm thấy thao tác."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError("Yêu cầu quá lớn hoặc không có nội dung.")
            request = json.loads(self.rfile.read(size).decode("utf-8"))
            self.send_json(200, run_demo(request))
        except (ValueError, UnicodeDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
        except (RuntimeError, subprocess.TimeoutExpired):
            self.send_json(500, {"error": "Demo chưa chạy được. Thử lại hoặc kiểm tra môi trường Python."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        parser.exit(1, f"Port {args.port} is busy. Try --port 8766.\n")
    print(f"LogiX VN demo: http://127.0.0.1:{server.server_port}", flush=True)
    print("Local / offline / isolated synthetic data. Ctrl+C to stop.", flush=True)
    if args.open:
        Timer(0.5, webbrowser.open, args=[f"http://127.0.0.1:{server.server_port}"]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
