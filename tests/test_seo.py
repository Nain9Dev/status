"""Search and AI-engine discoverability baseline for the generated status page."""

from __future__ import annotations

import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from scripts.monitor import generate_html_dashboard  # noqa: E402

HOST_ROOT = "https://status.naindev.com/"
AUTHOR_ID = "https://www.naindev.com/#person"

SAMPLE_REPORT = {
    "timestamp_iso": "2026-11-09T10:00:00Z",
    "total_services": 1,
    "operational_services": 1,
    "uptime_pct": 100.0,
    "services": [
        {
            "id": "svc-1",
            "name": "Service 1",
            "url": "https://svc1.naindev.com/",
            "category": "Backend",
            "description": "Backend engine",
            "status": "operational",
            "status_code": 200,
            "latency_ms": 40.0,
            "error": None,
        }
    ],
}


def read_root_file(name: str) -> str:
    with open(os.path.join(ROOT, name), "r", encoding="utf-8") as handle:
        return handle.read()


class TestGeneratedPageSeo(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = generate_html_dashboard(SAMPLE_REPORT)

    def meta(self, attribute: str, value: str) -> list[str]:
        pattern = rf'<meta\s+{attribute}="{re.escape(value)}"\s+content="([^"]*)"'
        return re.findall(pattern, self.html)

    def test_single_canonical_equals_host_root(self) -> None:
        hrefs = re.findall(r'<link\s+rel="canonical"\s+href="([^"]*)"', self.html)
        self.assertEqual(hrefs, [HOST_ROOT])

    def test_single_description_has_sensible_length(self) -> None:
        descriptions = self.meta("name", "description")
        self.assertEqual(len(descriptions), 1)
        self.assertTrue(70 <= len(descriptions[0]) <= 160, len(descriptions[0]))

    def test_open_graph_and_twitter_cards(self) -> None:
        self.assertEqual(self.meta("property", "og:type"), ["website"])
        self.assertEqual(self.meta("property", "og:url"), [HOST_ROOT])
        self.assertEqual(self.meta("property", "og:site_name"), ["NainDev Status"])
        self.assertEqual(len(self.meta("property", "og:title")), 1)
        self.assertEqual(
            self.meta("property", "og:description"), self.meta("name", "description")
        )
        images = self.meta("property", "og:image")
        self.assertEqual(len(images), 1)
        self.assertTrue(images[0].startswith("https://"))
        self.assertEqual(self.meta("name", "twitter:card"), ["summary_large_image"])
        self.assertEqual(self.meta("name", "twitter:image"), images)

    def test_author_link(self) -> None:
        self.assertIn('<link rel="author" href="https://www.naindev.com/">', self.html)

    def test_json_ld_software_application(self) -> None:
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', self.html, flags=re.DOTALL
        )
        self.assertEqual(len(blocks), 1)
        self.assertNotIn("<", blocks[0])
        data = json.loads(blocks[0])
        self.assertEqual(data["@type"], "SoftwareApplication")
        self.assertEqual(data["url"], HOST_ROOT)
        self.assertEqual(data["operatingSystem"], "Web")
        self.assertIs(data["isAccessibleForFree"], True)
        self.assertEqual(data["author"]["@id"], AUTHOR_ID)


class TestStaticRootFiles(unittest.TestCase):
    def test_robots_advertises_sitemap(self) -> None:
        lines = read_root_file("robots.txt").splitlines()
        self.assertIn("User-agent: *", lines)
        self.assertIn("Allow: /", lines)
        self.assertIn(f"Sitemap: {HOST_ROOT}sitemap.xml", lines)
        self.assertFalse(any(line.startswith("Disallow: /") for line in lines))

    def test_sitemap_lists_canonical_root(self) -> None:
        locations = re.findall(r"<loc>([^<]*)</loc>", read_root_file("sitemap.xml"))
        self.assertEqual(locations, [HOST_ROOT])

    def test_llms_txt_starts_with_h1(self) -> None:
        text = read_root_file("llms.txt")
        self.assertTrue(text.startswith("# "))
        self.assertIn("\n> ", text)


if __name__ == "__main__":
    unittest.main()
