# Claim Flow Studio

React + Vite + `@xyflow/react`, nối **backend Python thật** (`lab8.run_claim` qua `lab8.web_api`).

## Chạy (2 process)

```bash
# Terminal 1 — API (thư mục src/)
cd src
python -m lab8.web_api
# http://127.0.0.1:8765

# Terminal 2 — FE
cd src/web
npm install
npm run dev
# http://localhost:5173  (proxy /api → :8765)
```

Hard refresh: `Ctrl+Shift+R`. Badge **LIVE** = API online.

## API

| Method | Path | Mô tả |
| --- | --- | --- |
| GET | `/api/health` | Health |
| GET | `/api/claims` | Public claims (đã bỏ secret) |
| GET | `/api/shapes` | Danh sách shape + seed |
| POST | `/api/run` | `{ shape, claim_id, seed }` → `RunResult` + trace |

Mỗi lần run tạo SQLite tạm mới rồi gọi `run_shape` thật. Canvas replay theo **trace events** từ backend.

## UI

- Thu panel: `[` / `]` hoặc nút chrome
- Fullscreen canvas: nút expand
- Run live / Pause / Step / Reset
