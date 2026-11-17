"""Test nho: claim thieu order_id can bo sung thong tin, khong hoan tien."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from lab8.db import init_store
from lab8.shapes.workflow import run_claim


class WorkflowTest(unittest.TestCase):
    def test_missing_order_needs_info_without_refund(self):
        with TemporaryDirectory() as directory:
            store = Path(directory) / "store.sqlite"
            claim = {
                "claim_id": "C-TEST",
                "principal_id": "P-TEST",
                "order_id": None,
                "ticket": "Please check my order.",
                "parent_secret": "test-secret",
            }
            conn = init_store(
                store, {"orders": [], "policies": [], "approvals": []}, [claim]
            )
            conn.close()

            with (
                patch("lab8.shapes.workflow.tools.tool_cost", return_value=0),
                patch("lab8.trace.Trace.write", autospec=True) as write_trace,
            ):
                def save_trace(trace):
                    path = Path(directory) / "trace.json"
                    path.write_text(trace.dump(), encoding="utf-8")
                    return str(path)

                write_trace.side_effect = save_trace
                result = run_claim("C-TEST", seed=11, store_path=str(store))

            self.assertEqual(result.status, "needs_info")
            self.assertEqual(result.proposal_amount, 0)
            self.assertEqual(result.refund_effects, [])
            self.assertEqual(result.committed_audit_count, 0)
            trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
            self.assertEqual(trace["run_id"], result.run_id)


if __name__ == "__main__":
    unittest.main()
