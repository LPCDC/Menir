"""Tests for menir10_daily_report module."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.menir10_daily_report import build_daily_report


class TestDailyReport(unittest.TestCase):
    """Test daily report generation."""

    def test_build_daily_report_with_logs(self):
        """Test building a report from test logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            
            # Create test entries from two projects
            entries = [
                {
                    "interaction_id": "id1",
                    "project_id": "proj_a",
                    "intent_profile": "query",
                    "created_at": "2025-11-26T00:00:00+00:00",
                    "updated_at": "2025-11-26T00:00:00+00:00",
                    "flags": {},
                },
                {
                    "interaction_id": "id2",
                    "project_id": "proj_a",
                    "intent_profile": "response",
                    "created_at": "2025-11-26T00:01:00+00:00",
                    "updated_at": "2025-11-26T00:01:00+00:00",
                    "flags": {},
                },
                {
                    "interaction_id": "id3",
                    "project_id": "proj_b",
                    "intent_profile": "error",
                    "created_at": "2025-11-26T00:02:00+00:00",
                    "updated_at": "2025-11-26T00:02:00+00:00",
                    "flags": {},
                },
            ]
            
            # Write entries to JSONL
            with open(log_file, "w", encoding="utf-8") as f:
                for entry in entries:
                    json.dump(entry, f)
                    f.write("\n")
            
            # Build report
            report = build_daily_report(log_path=str(log_file), top_n=2, limit=10)
            
            # Assertions
            self.assertIsInstance(report, str)
            self.assertGreater(len(report), 0)
            self.assertIn("# Menir-10 Daily Context", report)
            self.assertIn("proj_a", report)

    def test_build_daily_report_no_logs(self):
        """Test building a report with no logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "empty.jsonl"
            
            report = build_daily_report(log_path=str(log_file), top_n=2, limit=10)
            
            self.assertEqual(report, "No Menir-10 logs found.")


if __name__ == "__main__":
    unittest.main()
