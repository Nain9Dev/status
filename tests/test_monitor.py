from __future__ import annotations

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.monitor import SERVICES, generate_html_dashboard, probe_service


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
        })

        self.assertEqual(result["status"], "operational")
        self.assertEqual(result["status_code"], 200)
        self.assertGreaterEqual(result["latency_ms"], 0.0)
        self.assertIsNone(result["error"])

    def test_generate_html_dashboard(self):
        mock_data = {
            "timestamp_iso": "2026-10-15T18:00:00Z",
            "total_services": 2,
            "operational_services": 2,
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
                    "status": "operational",
                    "status_code": 200,
                    "latency_ms": 55.1,
                    "error": None
                }
            ]
        }

        html = generate_html_dashboard(mock_data)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("NainDev Platform Status", html)
        self.assertIn("All Systems Operational", html)
        self.assertIn("Test Service 1", html)
        self.assertIn("Test Service 2", html)
        self.assertIn("https://test1.naindev.com/", html)


if __name__ == "__main__":
    unittest.main()
