"""Tests for menir10_boot module."""

import json
import os
import tempfile
import unittest
from pathlib import Path

import menir10.menir10_log
from menir10.menir10_boot import (
    get_default_project_id,
    start_boot_interaction,
    complete_boot_interaction,
)


class TestBootHelper(unittest.TestCase):
    """Test boot helper functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_log_path = menir10.menir10_log.LOG_PATH
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir_path = Path(self.tmpdir.name)
        self.log_file = self.tmpdir_path / "menir10_interactions.jsonl"
        menir10.menir10_log.LOG_PATH = self.log_file
        
        self.original_env = os.environ.get("MENIR_PROJECT_ID")

    def tearDown(self):
        """Clean up test fixtures."""
        menir10.menir10_log.LOG_PATH = self.original_log_path
        if self.original_env is not None:
            os.environ["MENIR_PROJECT_ID"] = self.original_env
        elif "MENIR_PROJECT_ID" in os.environ:
            del os.environ["MENIR_PROJECT_ID"]
        self.tmpdir.cleanup()

    def test_get_default_project_id_from_env(self):
        """Test getting project ID from environment."""
        os.environ["MENIR_PROJECT_ID"] = "test_proj"
        result = get_default_project_id()
        self.assertEqual(result, "test_proj")

    def test_get_default_project_id_fallback(self):
        """Test getting default project ID when env not set."""
        if "MENIR_PROJECT_ID" in os.environ:
            del os.environ["MENIR_PROJECT_ID"]
        result = get_default_project_id()
        self.assertEqual(result, "personal")

    def test_start_boot_interaction_logs_entry(self):
        """Test that start_boot_interaction creates a log entry."""
        os.environ["MENIR_PROJECT_ID"] = "test_menir10"
        
        state = start_boot_interaction()
        
        self.assertIsNotNone(state.created_at)
        self.assertIsNotNone(state.updated_at)
        self.assertEqual(state.project_id, "test_menir10")
        self.assertEqual(state.intent_profile, "boot_now")
        
        # Check log file exists and has entry
        self.assertTrue(self.log_file.exists())
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertGreater(len(lines), 0)
        
        entry = json.loads(lines[0])
        self.assertEqual(entry["project_id"], "test_menir10")
        self.assertEqual(entry["metadata"]["stage"], "start")

    def test_complete_boot_interaction_logs_entry(self):
        """Test that complete_boot_interaction creates a log entry."""
        os.environ["MENIR_PROJECT_ID"] = "test_menir10"
        
        state = start_boot_interaction()
        complete_boot_interaction(state, status="ok", extra={"probe": True})
        
        # Check log file has two entries
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)
        
        # Check completion entry
        entry = json.loads(lines[1])
        self.assertEqual(entry["project_id"], "test_menir10")
        self.assertEqual(entry["metadata"]["stage"], "complete")
        self.assertEqual(entry["metadata"]["status"], "ok")
        self.assertTrue(entry["metadata"]["probe"])


if __name__ == "__main__":
    unittest.main()
