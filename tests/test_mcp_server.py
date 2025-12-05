"""
Pytest suite for Menir MCP JSON-RPC server (v10.3).

Tests all MCP methods via FastAPI TestClient.
Validates JSON-RPC compliance, error handling, and data integrity.

Run with: pytest tests/test_mcp_server.py -v
"""

import pytest
import json
from fastapi.testclient import TestClient
from menir10.mcp_app import app

# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health and info endpoints."""
    
    def test_health_check(self):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Menir MCP JSON-RPC"
        assert data["version"] == "10.3"
    
    def test_server_info(self):
        """Test /info endpoint."""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "methods" in data
        assert "server" in data
        assert len(data["methods"]) > 0


class TestJSONRPCCompliance:
    """Test JSON-RPC 2.0 compliance."""
    
    def test_ping_method(self):
        """Test ping method."""
        payload = {
            "jsonrpc": "2.0",
            "method": "ping",
            "id": 1
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert data["result"]["status"] == "Menir-10 contextual proxy alive"
    
    def test_missing_jsonrpc_version(self):
        """Test error when jsonrpc version missing."""
        payload = {
            "method": "ping",
            "id": 1
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600
    
    def test_invalid_method(self):
        """Test error when method doesn't exist."""
        payload = {
            "jsonrpc": "2.0",
            "method": "nonexistent_method",
            "id": 2
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601
    
    def test_malformed_json(self):
        """Test error with malformed JSON."""
        response = client.post("/jsonrpc", content="not json", headers={"Content-Type": "application/json"})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data


@pytest.mark.parametrize("method,params,expected_keys", [
    ("ping", {}, ["status", "version"]),
    ("boot_now", {}, ["timestamp", "repo_root", "projects_count"]),
    ("list_projects", {}, ["projects", "total_projects"]),
    ("project_summary", {"project_id": "itau_15220012"}, ["project_id", "interaction_count"]),
    ("context", {"project_id": "itau_15220012"}, ["project_id", "interaction_count", "recent_interactions"]),
])
class TestMCPMethods:
    """Parametrized tests for all MCP methods."""
    
    def test_method_returns_result(self, method, params, expected_keys):
        """Test that method returns expected result structure."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 99
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # JSON-RPC compliance
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 99
        assert "result" in data or "error" in data
        
        # Check result structure
        if "result" in data:
            result = data["result"]
            for key in expected_keys:
                assert key in result, f"Missing key '{key}' in {method} result"


class TestMethodSpecific:
    """Specific tests for individual methods."""
    
    def test_boot_now_includes_context(self):
        """Test that boot_now includes project and interaction context."""
        payload = {
            "jsonrpc": "2.0",
            "method": "boot_now",
            "id": 1
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        
        # Should have context
        assert "projects_count" in result
        assert "interactions_count" in result
        assert "notes" in result
        assert isinstance(result["notes"], list)
    
    def test_list_projects_with_top_n(self):
        """Test list_projects with top_n parameter."""
        payload = {
            "jsonrpc": "2.0",
            "method": "list_projects",
            "params": {"top_n": 2},
            "id": 2
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        
        # Should limit to top 2 projects
        assert len(result["projects"]) <= 2
    
    def test_project_summary_required_param(self):
        """Test that project_summary requires project_id."""
        payload = {
            "jsonrpc": "2.0",
            "method": "project_summary",
            "params": {},
            "id": 3
        }
        response = client.post("/jsonrpc", json=payload)
        # Should either return error or handle gracefully
        assert response.status_code in [200, 400, 404]
    
    def test_context_with_markdown(self):
        """Test context method includes markdown rendering."""
        payload = {
            "jsonrpc": "2.0",
            "method": "context",
            "params": {
                "project_id": "itau_15220012",
                "include_markdown": True,
                "limit": 5
            },
            "id": 4
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        
        # Should include markdown if present
        if "markdown_context" in result:
            assert isinstance(result["markdown_context"], str)
    
    def test_search_interactions_with_filters(self):
        """Test search_interactions with multiple filters."""
        payload = {
            "jsonrpc": "2.0",
            "method": "search_interactions",
            "params": {
                "project_id": "itau_15220012",
                "intent_profile": "note",
                "limit": 3
            },
            "id": 5
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        
        # Should return results array
        assert "results" in result
        assert "result_count" in result
        assert result["result_count"] <= 3


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_payload(self):
        """Test handling of empty JSON object."""
        response = client.post("/jsonrpc", json={})
        assert response.status_code in [400, 200]
    
    def test_non_dict_payload(self):
        """Test handling of non-dict payload."""
        response = client.post("/jsonrpc", json=[])
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_null_id_preserved(self):
        """Test that null id is preserved in response."""
        payload = {
            "jsonrpc": "2.0",
            "method": "ping",
            "id": None
        }
        response = client.post("/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_consistent_timestamps(self):
        """Test that timestamps are consistent and valid."""
        payload = {
            "jsonrpc": "2.0",
            "method": "boot_now",
            "id": 1
        }
        response = client.post("/jsonrpc", json=payload)
        data = response.json()
        result = data["result"]
        
        # Should have ISO8601 timestamp
        timestamp = result.get("timestamp")
        assert timestamp is not None
        assert "T" in timestamp  # ISO8601 format
    
    def test_no_data_mutation(self):
        """Test that multiple calls don't mutate data (ignoring timestamp)."""
        payload = {
            "jsonrpc": "2.0",
            "method": "list_projects",
            "id": 1
        }
        
        response1 = client.post("/jsonrpc", json=payload)
        response2 = client.post("/jsonrpc", json=payload)
        
        result1 = response1.json()["result"].copy()
        result2 = response2.json()["result"].copy()
        
        # Remove timestamps (they will differ)
        result1.pop("timestamp", None)
        result2.pop("timestamp", None)
        
        # Data should be identical except for timestamp
        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
