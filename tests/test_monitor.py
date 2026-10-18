from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.monitor import (
    SERVICES,
    generate_html_dashboard,
    probe_all_services,
    probe_service,
    update_history_and_compute_uptime,
)


class TestMonitor(unittest.TestCase):
    def test_services_catalog_completeness(self):
        """Validates that all essential services are declared with proper metadata."""
        self.assertGreaterEqual(len(SERVICES), 15)
        for s in SERVICES:
            self.assertIn("id", s)
            self.assertIn("name", s)
            self.assertIn("url", s)
            self.assertTrue(s["url"].startswith("https://"))
            self.assertIn("category", s)
            self.assertIn("description", s)

    @patch("urllib.request.urlopen")
    def test_probe_service_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        result = probe_service({
            "id": "test",
            "name": "Test Service",
            "url": "https://test.naindev.com/",
            "category": "Test",
            "description": "Test description"
        }, timeout_seconds=2.0, max_retries=2, retry_delay_seconds=0.01)

        self.assertEqual(result["status"], "operational")
        self.assertEqual(result["status_code"], 200)
        self.assertGreaterEqual(result["latency_ms"], 0.0)
        self.assertIsNone(result["error"])
        self.assertEqual(result["retries"], 0)

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_probe_service_retry_on_transient_failure(self, mock_urlopen, mock_sleep):
        """Verifies that a first network failure is retried and recovers cleanly."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        # First attempt raises URLError, second attempt succeeds
        mock_urlopen.side_effect = [
            ConnectionResetError("Connection reset by peer"),
            mock_resp
        ]

        result = probe_service({
            "id": "transient",
            "name": "Transient Service",
            "url": "https://transient.naindev.com/",
            "category": "Test",
            "description": "Transient test"
        }, timeout_seconds=2.0, max_retries=2, retry_delay_seconds=0.01)

        self.assertEqual(result["status"], "operational")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["retries"], 1)
        self.assertEqual(mock_sleep.call_count, 1)

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_probe_service_persistent_failure(self, mock_urlopen, mock_sleep):
        """Verifies that multiple consecutive failures result in status down."""
        mock_urlopen.side_effect = TimeoutError("Gateway timed out")

        result = probe_service({
            "id": "down-service",
            "name": "Failing Service",
            "url": "https://fail.naindev.com/",
            "category": "Test",
            "description": "Failing test"
        }, timeout_seconds=2.0, max_retries=2, retry_delay_seconds=0.01)

        self.assertEqual(result["status"], "down")
        self.assertEqual(result["status_code"], 0)
        self.assertIn("Gateway timed out", result["error"])
        self.assertEqual(result["retries"], 1)

    @patch("scripts.monitor.probe_service")
    def test_probe_all_services_concurrency_and_ordering(self, mock_probe_service):
        """Verifies concurrent execution preserves the exact input ordering."""
        def side_effect_probe(s, *args, **kwargs):
            return {
                "id": s["id"],
                "name": s["name"],
                "url": s["url"],
                "category": s["category"],
                "description": s["description"],
                "status": "operational",
                "status_code": 200,
                "latency_ms": 10.0,
                "error": None,
                "retries": 0,
            }

        mock_probe_service.side_effect = side_effect_probe

        sample_services = [
            {"id": f"srv-{i}", "name": f"Service {i}", "url": f"https://s{i}.com/", "category": "C", "description": "D"}
            for i in range(10)
        ]

        results = probe_all_services(sample_services, max_workers=4)
        self.assertEqual(len(results), 10)
        for i, res in enumerate(results):
            self.assertEqual(res["id"], f"srv-{i}")

    def test_update_history_and_compute_uptime(self):
        """Verifies that history updates correctly and computes measured uptime percentage."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            history_file = os.path.join(tmp_dir, "history.json")

            # Entry 1: 10/10 operational -> 100%
            uptime1 = update_history_and_compute_uptime(
                history_file_path=history_file,
                current_timestamp="2026-10-17T12:00:00Z",
                total_services=10,
                operational_services=10,
                avg_latency_ms=100.0,
                max_history_entries=5,
            )
            self.assertEqual(uptime1, 100.0)

            # Entry 2: 8/10 operational -> 18/20 = 90.0%
            uptime2 = update_history_and_compute_uptime(
                history_file_path=history_file,
                current_timestamp="2026-10-17T12:30:00Z",
                total_services=10,
                operational_services=8,
                avg_latency_ms=120.0,
                max_history_entries=5,
            )
            self.assertEqual(uptime2, 90.0)

            with open(history_file, "r", encoding="utf-8") as f:
                history_data = json.load(f)
            self.assertEqual(len(history_data), 2)

    def test_generate_html_dashboard(self):
        mock_data = {
            "timestamp_iso": "2026-10-17T18:00:00Z",
            "total_services": 2,
            "operational_services": 2,
            "uptime_pct": 99.95,
            "services": [
                {
                    "id": "test-1",
                    "name": "Test Service 1",
                    "url": "https://test1.naindev.com/",
                    "category": "Backend",
                    "description": "Backend engine",
                    "status": "operational",
                    "status_code": 200,
                    "latency_ms": 42.5,
                    "error": None
                },
                {
                    "id": "test-2",
                    "name": "Test Service 2",
                    "url": "https://test2.naindev.com/",
                    "category": "3D",
                    "description": "3D viewer",
                    "status": "degraded",
                    "status_code": 403,
                    "latency_ms": 55.1,
                    "error": "Forbidden"
                }
            ]
        }

        html = generate_html_dashboard(mock_data)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("NainDev Platform Status", html)
        self.assertIn("1 System(s) Experiencing Issues", html)
        self.assertIn("99.95%", html)
        self.assertIn("Test Service 1", html)
        self.assertIn("Test Service 2", html)
        self.assertIn("https://test1.naindev.com/", html)

    def test_should_commit_triggers_on_manual_events(self):
        """Verifies should_commit returns true when triggered by push or workflow_dispatch."""
        from scripts.should_commit import should_commit

        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "workflow_dispatch"}):
            self.assertTrue(should_commit())

        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "push"}):
            self.assertTrue(should_commit())

    def test_should_commit_triggers_on_outage(self):
        """Verifies should_commit returns true when any service is down."""
        from scripts.should_commit import should_commit

        with tempfile.TemporaryDirectory() as tmp_dir:
            status_file = os.path.join(tmp_dir, "status.json")
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump({"total_services": 17, "operational_services": 16}, f)

            with patch("scripts.should_commit.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
                    {"total_services": 17, "operational_services": 16}
                )
                with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule"}):
                    self.assertTrue(should_commit())


if __name__ == "__main__":
    unittest.main()

