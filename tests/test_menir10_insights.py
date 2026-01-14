"""Tests for menir10_insights module."""

import unittest

from menir10.menir10_insights import (
    get_logs,
    group_by_project,
    list_top_projects,
    summarize_project,
    render_project_context,
)


class TestInsights(unittest.TestCase):
    """Test insights functions."""

    def setUp(self):
        """Create test log data."""
        self.logs = [
            {
                "interaction_id": "i1",
                "project_id": "proj_x",
                "intent_profile": "greeting",
                "created_at": "2025-11-26T00:00:00+00:00",
                "updated_at": "2025-11-26T00:00:00+00:00",
                "flags": {},
            },
            {
                "interaction_id": "i2",
                "project_id": "proj_x",
                "intent_profile": "query",
                "created_at": "2025-11-26T00:01:00+00:00",
                "updated_at": "2025-11-26T00:01:00+00:00",
                "flags": {"active": True},
            },
            {
                "interaction_id": "i3",
                "project_id": "proj_y",
                "intent_profile": "error",
                "created_at": "2025-11-26T00:02:00+00:00",
                "updated_at": "2025-11-26T00:02:00+00:00",
                "flags": {},
            },
        ]

    def test_group_by_project(self):
        """Test grouping logs by project."""
        grouped = group_by_project(self.logs)
        
        self.assertIn("proj_x", grouped)
        self.assertIn("proj_y", grouped)
        self.assertEqual(len(grouped["proj_x"]), 2)
        self.assertEqual(len(grouped["proj_y"]), 1)

    def test_list_top_projects(self):
        """Test listing top projects."""
        top = list_top_projects(self.logs, top_n=2)
        
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0], ("proj_x", 2))
        self.assertEqual(top[1], ("proj_y", 1))

    def test_summarize_project(self):
        """Test project summarization."""
        summary = summarize_project("proj_x", self.logs, limit=10)
        
        self.assertEqual(summary["project_id"], "proj_x")
        self.assertEqual(summary["total_count"], 2)
        self.assertEqual(summary["sample_count"], 2)
        self.assertEqual(len(summary["interactions"]), 2)

    def test_summarize_project_with_limit(self):
        """Test project summarization with limit."""
        summary = summarize_project("proj_x", self.logs, limit=1)
        
        self.assertEqual(summary["total_count"], 2)
        self.assertEqual(summary["sample_count"], 1)
        self.assertEqual(len(summary["interactions"]), 1)

    def test_render_project_context(self):
        """Test rendering project context."""
        summary = summarize_project("proj_x", self.logs, limit=10)
        context = render_project_context(summary)
        
        self.assertIsInstance(context, str)
        self.assertIn("proj_x", context)
        self.assertIn("greeting", context)
        self.assertIn("query", context)
        self.assertGreater(len(context), 0)

    def test_render_project_context_empty(self):
        """Test rendering context for project with no interactions."""
        summary = summarize_project("nonexistent", self.logs, limit=10)
        context = render_project_context(summary)
        
        self.assertIn("nonexistent", context)
        self.assertIn("no interactions", context)


if __name__ == "__main__":
    unittest.main()
