"""Install contract of the status page (specs/next-pwa-install, INS-001 to INS-007).

Covers the web app manifest, the install icons and the head tags a phone needs to install the page.
Standard library only: the icons are decoded with zlib and struct, so the suite gains no image dependency.
"""

from __future__ import annotations

import json
import math
import os
import re
import struct
import sys
import unittest
import zlib
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from scripts.monitor import generate_html_dashboard  # noqa: E402

APP_NAME = "NainDev Status"
APP_SHORT_NAME = "NainStatus"
PAGE_BACKGROUND = "#07090e"
MANIFEST = "./manifest.webmanifest"
APPLE_TOUCH_ICON = "./icons/apple-touch-icon.png"
MASKABLE_ICON = "./icons/icon-maskable-512.png"
EXPECTED_ICONS = [
    {"src": "./icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "./icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": MASKABLE_ICON, "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# A launcher may crop a maskable icon to a centred circle of this radius, as a fraction of the width.
SAFE_ZONE_RADIUS = 0.4
# Largest channel distance from the background at which a pixel still counts as background, not as mark.
BACKGROUND_TOLERANCE = 24

SAMPLE_REPORT = {
    "timestamp_iso": "2026-11-13T10:00:00Z",
    "total_services": 0,
    "operational_services": 0,
    "uptime_pct": 100.0,
    "services": [],
}


def site_file(reference: str) -> str:
    """Maps a URL reference of the page or the manifest, both at the site root, to a file of the repository."""
    return os.path.normpath(os.path.join(ROOT, *reference.split("/")))


def read_site_file(reference: str) -> bytes:
    with open(site_file(reference), "rb") as handle:
        return handle.read()


def png_size(data: bytes) -> tuple[int, int]:
    """Reads the pixel size from the IHDR chunk, the first chunk of every PNG file."""
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        raise ValueError("not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def undo_filter(kind: int, line: bytearray, above: bytes, step: int) -> None:
    """Reverses the filter of one PNG scanline in place; `step` is the number of bytes per pixel."""
    if kind == 0:
        return
    if kind > 4:
        raise ValueError(f"unknown PNG filter {kind}")
    for index in range(len(line)):
        left = line[index - step] if index >= step else 0
        up = above[index]
        if kind == 1:
            predictor = left
        elif kind == 2:
            predictor = up
        elif kind == 3:
            predictor = (left + up) // 2
        else:
            corner = above[index - step] if index >= step else 0
            estimate = left + up - corner
            # Paeth: the neighbour closest to the estimate; ties go to left, then up, then the corner.
            _, _, predictor = min(
                (abs(estimate - left), 0, left), (abs(estimate - up), 1, up), (abs(estimate - corner), 2, corner)
            )
        line[index] = (line[index] + predictor) & 0xFF


def read_png(data: bytes) -> tuple[int, int, int, list[bytes]]:
    """Decodes an 8-bit RGB or RGBA PNG into (width, height, channels, rows)."""
    width, height = png_size(data)
    bit_depth, colour_type, _, _, interlace = struct.unpack(">5B", data[24:29])
    channels = {2: 3, 6: 4}.get(colour_type)
    compressed = []
    position = 8
    while position < len(data):
        length, kind = struct.unpack(">I4s", data[position:position + 8])
        if kind == b"IDAT":
            compressed.append(data[position + 8:position + 8 + length])
        elif kind == b"tRNS":
            # A transparent colour key would make an RGB file see-through with no alpha channel to count.
            channels = None
        position += length + 12
    if bit_depth != 8 or channels is None or interlace:
        raise ValueError("only 8-bit RGB or RGBA PNG files with no interlacing and no tRNS chunk are read here")
    stride = width * channels
    raw = zlib.decompress(b"".join(compressed))
    rows: list[bytes] = []
    above = bytes(stride)
    for start in range(0, height * (stride + 1), stride + 1):
        line = bytearray(raw[start + 1:start + 1 + stride])
        undo_filter(raw[start], line, above, channels)
        above = bytes(line)
        rows.append(above)
    return width, height, channels, rows


def transparent_pixels(channels: int, rows: list[bytes]) -> int:
    """Counts the pixels that are not fully opaque; an RGB file has no alpha channel and so has none."""
    if channels == 3:
        return 0
    return sum(len(row) // 4 - row[3::4].count(255) for row in rows)


class HeadTags(HTMLParser):
    """Collects the language of a page and the attributes of the link and meta tags of its head."""

    def __init__(self) -> None:
        super().__init__()
        self.language: str | None = None
        self.in_head = False
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "html":
            self.language = dict(attrs).get("lang")
        elif tag == "head":
            self.in_head = True
        elif self.in_head and tag in ("link", "meta"):
            self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.in_head = False

    def links(self, rel: str) -> list[dict[str, str | None]]:
        return [attrs for tag, attrs in self.tags if tag == "link" and attrs.get("rel") == rel]

    def meta(self, name: str) -> list[str | None]:
        return [attrs.get("content") for tag, attrs in self.tags if tag == "meta" and attrs.get("name") == name]


class InstallContractCase(unittest.TestCase):
    """Loads the manifest of the repository and the page the monitor writes."""

    manifest: dict
    html: str
    page: HeadTags

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(read_site_file(MANIFEST))
        cls.html = generate_html_dashboard(SAMPLE_REPORT)
        cls.page = HeadTags()
        cls.page.feed(cls.html)


class TestManifest(InstallContractCase):
    def test_names_the_app_and_opens_it_standalone_from_the_site_root(self) -> None:
        """INS-002: fixed names, a standalone window and one identity at the root of the site."""
        self.assertEqual(self.manifest["name"], APP_NAME)
        self.assertEqual(self.manifest["short_name"], APP_SHORT_NAME)
        self.assertLessEqual(len(self.manifest["short_name"]), 12, "a longer label is truncated under the icon")
        self.assertEqual(self.manifest["display"], "standalone")
        self.assertEqual(self.manifest["start_url"], "./")
        self.assertEqual(self.manifest["id"], self.manifest["start_url"])
        self.assertEqual(self.manifest["scope"], "./")
        self.assertEqual(self.manifest["dir"], "ltr")
        self.assertNotIn(
            "prefer_related_applications", self.manifest, "a related native app would cancel the browser install"
        )

    def test_repeats_the_language_description_and_background_of_the_page(self) -> None:
        """INS-002: the manifest describes the page with the page's own words and colour."""
        self.assertEqual(self.manifest["lang"], "en")
        self.assertEqual(self.manifest["lang"], self.page.language)
        self.assertEqual([self.manifest["description"]], self.page.meta("description"))
        self.assertEqual(self.manifest["theme_color"], PAGE_BACKGROUND)
        self.assertEqual(self.manifest["background_color"], PAGE_BACKGROUND)

    def test_declares_192_and_512_px_icons_and_a_maskable_one(self) -> None:
        """INS-003: the sizes Chrome asks for, one purpose per entry."""
        declared = [
            {member: icon.get(member) for member in ("src", "sizes", "type", "purpose")}
            for icon in self.manifest["icons"]
        ]
        self.assertEqual(declared, EXPECTED_ICONS)


class TestInstallIcons(InstallContractCase):
    def test_every_declared_icon_is_a_png_of_the_declared_size(self) -> None:
        """INS-003: each icon file exists and measures what the manifest declares."""
        self.assertEqual(len(self.manifest["icons"]), len(EXPECTED_ICONS))
        for icon in self.manifest["icons"]:
            with self.subTest(icon=icon["src"]):
                width, height = png_size(read_site_file(icon["src"]))
                self.assertEqual(f"{width}x{height}", icon["sizes"])

    def test_maskable_icon_is_opaque_and_keeps_the_mark_in_the_safe_zone(self) -> None:
        """INS-004: a launcher fills transparent pixels with its own colour and crops to a circle."""
        width, height, channels, rows = read_png(read_site_file(MASKABLE_ICON))
        self.assertEqual(transparent_pixels(channels, rows), 0, "transparent pixels in the maskable icon")
        background = rows[0][:3]
        centre = width / 2
        mark = 0
        outside: list[tuple[int, int]] = []
        for y, row in enumerate(rows):
            for x in range(width):
                pixel = row[x * channels:x * channels + 3]
                if max(abs(value - base) for value, base in zip(pixel, background)) <= BACKGROUND_TOLERANCE:
                    continue
                mark += 1
                if math.hypot(x + 0.5 - centre, y + 0.5 - centre) > width * SAFE_ZONE_RADIUS:
                    outside.append((x, y))
        self.assertEqual(outside[:5], [], f"{len(outside)} pixels of the mark would be cut by a circular mask")
        self.assertGreater(mark, width * height * 0.02, "the maskable icon must carry the mark")

    def test_apple_touch_icon_is_180_px_and_opaque(self) -> None:
        """INS-004 and INS-005: iOS takes this file as the home screen icon and paints transparency black."""
        width, height, channels, rows = read_png(read_site_file(APPLE_TOUCH_ICON))
        self.assertEqual((width, height), (180, 180))
        self.assertEqual(transparent_pixels(channels, rows), 0, "transparent pixels in the Apple touch icon")


class TestGeneratedPageInstallTags(InstallContractCase):
    def test_links_the_published_manifest_once(self) -> None:
        """INS-001: the page the monitor writes links the manifest of the site root exactly once."""
        self.assertEqual([link.get("href") for link in self.page.links("manifest")], [MANIFEST])

    def test_carries_the_ios_tags(self) -> None:
        """INS-005: icon, label and standalone window on iOS."""
        self.assertEqual(
            [(link.get("sizes"), link.get("href")) for link in self.page.links("apple-touch-icon")],
            [("180x180", APPLE_TOUCH_ICON)],
        )
        self.assertEqual(self.page.meta("apple-mobile-web-app-title"), [self.manifest["short_name"]])
        self.assertEqual(self.page.meta("mobile-web-app-capable"), ["yes"])
        self.assertEqual(self.page.meta("apple-mobile-web-app-capable"), ["yes"])
        self.assertEqual(self.page.meta("apple-mobile-web-app-status-bar-style"), ["black"])

    def test_theme_colour_matches_the_manifest_and_the_page_background(self) -> None:
        """INS-006: one colour for the browser bar, the splash screen and the first paint of the page."""
        self.assertEqual(self.page.meta("theme-color"), [self.manifest["theme_color"]])
        self.assertEqual(re.findall(r"--bg:\s*(#[0-9a-fA-F]{6});", self.html), [self.manifest["background_color"]])


if __name__ == "__main__":
    unittest.main()
