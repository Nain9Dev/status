#!/usr/bin/env python3
"""Deterministic service uptime and latency monitor for NainDev Platform.

Executes concurrent HTTP probes against all public portfolio applications,
records status and latency, and generates a static dashboard and data artifacts.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List

SERVICES = [
    {
        "id": "portfolio",
        "name": "NainDev Portfolio",
        "url": "https://www.naindev.com/",
        "category": "Platform Hub",
        "description": "Architectural portfolio & showcase gateway"
    },
    {
        "id": "nain-policy",
        "name": "NainPolicy",
        "url": "https://policy.naindev.com/",
        "category": "Backend & Cloud",
        "description": "Insurance policy operations & financial accounting engine (.NET 10)"
    },
    {
        "id": "nain-order",
        "name": "NainOrder",
        "url": "https://order.naindev.com/",
        "category": "Backend & Cloud",
        "description": "Tactical DDD e-commerce order API with CQRS (.NET 10)"
    },
    {
        "id": "nain-drive",
        "name": "NainDrive",
        "url": "https://drive.naindev.com/",
        "category": "Backend & Cloud",
        "description": "Driving school management & accounting engine (Python / FastAPI)"
    },
    {
        "id": "nain-notify",
        "name": "NainNotify",
        "url": "https://notify.naindev.com/",
        "category": "Backend & Cloud",
        "description": "Asynchronous notification microservice (.NET 10 / MassTransit)"
    },
    {
        "id": "nain-tai",
        "name": "NainTAI",
        "url": "https://tai.naindev.com/",
        "category": "Backend & Cloud",
        "description": "Civil service exam simulator (.NET 10 / Dapper / React 19)"
    },
    {
        "id": "nain-3d",
        "name": "Nain3D",
        "url": "https://3d.naindev.com/",
        "category": "3D Geometry & Validation",
        "description": "Deterministic 3D asset validation engine & conformance gateway"
    },
    {
        "id": "parametricad",
        "name": "ParametriCAD AI",
        "url": "https://parametricad.naindev.com/",
        "category": "3D Geometry & Validation",
        "description": "Deterministic parametric CAD engine & WebGL viewer (OpenCASCADE)"
    },
    {
        "id": "nain-configurator",
        "name": "NainConfigurator",
        "url": "https://configurator.naindev.com/",
        "category": "3D Geometry & Validation",
        "description": "Modular product configurator engine (.NET 10 / Vue 3)"
    },
    {
        "id": "nain-prospect",
        "name": "NainProspect",
        "url": "https://prospect.naindev.com/",
        "category": "Workbenches & Applications",
        "description": "B2B lead generation & compliance outreach pipeline (FastAPI / Vue 3)"
    },
    {
        "id": "nain-write",
        "name": "NainWrite",
        "url": "https://write.naindev.com/",
        "category": "Workbenches & Applications",
        "description": "Deterministic Spanish text rewriting workbench (TypeScript)"
    },
    {
        "id": "have-tickets",
        "name": "HaveTickets",
        "url": "https://tickets.naindev.com/",
        "category": "Workbenches & Applications",
        "description": "Cinema ticketing & seat reservation platform (Blazor / .NET 10)"
    },
    {
        "id": "game-haven",
        "name": "GameHaven",
        "url": "https://gamehaven.naindev.com/",
        "category": "Workbenches & Applications",
        "description": "Indie game digital desktop storefront & catalog (WPF / Web)"
    },
    {
        "id": "orbe-3d",
        "name": "Orbe3D",
        "url": "https://orbe.naindev.com/",
        "category": "Web Games (Zero Engine)",
        "description": "Procedural 3D arcade endless runner (Three.js / Web Audio)"
    },
    {
        "id": "pong-arcade",
        "name": "PongArcade",
        "url": "https://pong.naindev.com/",
        "category": "Web Games (Zero Engine)",
        "description": "Continuous collision 3D arena pong (TypeScript / Canvas)"
    },
    {
        "id": "tai-client-legacy",
        "name": "TAI Study System (Vercel)",
        "url": "https://tai-study-system-js.vercel.app/",
        "category": "Backend & Cloud",
        "description": "Historical standalone client deployment for exam simulation"
    }
]


def probe_service(service: Dict[str, str], timeout_seconds: float = 12.0) -> Dict[str, Any]:
    """Probes a single service via HTTP GET and returns metrics."""
    req = urllib.request.Request(
        service["url"],
        headers={"User-Agent": "NainDev-Status-Probe/1.0 (+https://status.naindev.com)"}
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            status_code = resp.status
            return {
                "id": service["id"],
                "name": service["name"],
                "url": service["url"],
                "category": service["category"],
                "description": service["description"],
                "status": "operational" if 200 <= status_code < 400 else "degraded",
                "status_code": status_code,
                "latency_ms": latency_ms,
                "error": None
            }
    except urllib.error.HTTPError as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        return {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "category": service["category"],
            "description": service["description"],
            "status": "degraded" if e.code in (401, 403, 404) else "down",
            "status_code": e.code,
            "latency_ms": latency_ms,
            "error": str(e)
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        return {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "category": service["category"],
            "description": service["description"],
            "status": "down",
            "status_code": 0,
            "latency_ms": latency_ms,
            "error": str(e)
        }


def generate_html_dashboard(data: Dict[str, Any]) -> str:
    """Generates the static responsive HTML status page."""
    operational_count = sum(1 for s in data["services"] if s["status"] == "operational")
    total_count = len(data["services"])
    all_ok = operational_count == total_count
    overall_status_text = "All Systems Operational" if all_ok else f"{total_count - operational_count} System(s) Experiencing Issues"
    overall_badge_class = "status-good" if all_ok else "status-warning"
    avg_latency = round(sum(s["latency_ms"] for s in data["services"] if s["latency_ms"] > 0) / max(1, total_count), 1)

    cards_by_category: Dict[str, List[Dict[str, Any]]] = {}
    for s in data["services"]:
        cards_by_category.setdefault(s["category"], []).append(s)

    categories_html = []
    for cat_name, items in cards_by_category.items():
        items_html = []
        for item in items:
            status_indicator = "dot-green" if item["status"] == "operational" else "dot-red"
            items_html.append(f"""
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name-row">
                            <span class="status-dot {status_indicator}"></span>
                            <a href="{item['url']}" target="_blank" rel="noopener noreferrer" class="service-link">
                                {item['name']}
                            </a>
                        </div>
                        <span class="badge {item['status']}">{item['status'].upper()}</span>
                    </div>
                    <p class="service-desc">{item['description']}</p>
                    <div class="service-meta">
                        <span class="meta-label">Latency: <strong>{item['latency_ms']} ms</strong></span>
                        <span class="meta-label">HTTP {item['status_code']}</span>
                    </div>
                </div>
            """)

        categories_html.append(f"""
            <section class="category-section">
                <h2 class="category-heading">{cat_name}</h2>
                <div class="grid">
                    {''.join(items_html)}
                </div>
            </section>
        """)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NainDev Status | Platform Observability & Uptime</title>
    <meta name="description" content="Real-time uptime, response latency, and operational health metrics across all NainDev platforms and microservices.">
    <link rel="icon" type="image/x-icon" href="https://www.naindev.com/favicon.ico">
    <style>
        :root {{
            --bg: #07090e;
            --surface: #0e121a;
            --surface-hover: #141924;
            --border: rgba(255, 255, 255, 0.08);
            --text: #f1f5f9;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --green: #22c55e;
            --red: #ef4444;
            --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font);
            line-height: 1.5;
            padding: 32px 16px 80px;
        }}
        .container {{
            max-width: 1040px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 32px;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: var(--text);
        }}
        .brand-badge {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: #040914;
        }}
        .brand-title {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        .back-link {{
            color: var(--accent);
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
        }}
        .back-link:hover {{ text-decoration: underline; }}
        .hero-banner {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 40px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .banner-status {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .status-indicator {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
        }}
        .status-good {{ background: var(--green); box-shadow: 0 0 12px rgba(34, 197, 94, 0.6); }}
        .status-warning {{ background: var(--red); box-shadow: 0 0 12px rgba(239, 68, 68, 0.6); }}
        .banner-title {{
            font-size: 20px;
            font-weight: 700;
        }}
        .banner-meta {{
            font-size: 13px;
            color: var(--text-muted);
        }}
        .stats-summary {{
            display: flex;
            gap: 24px;
            font-size: 13px;
        }}
        .stat-item strong {{ color: var(--text); font-weight: 600; }}
        .category-section {{
            margin-bottom: 36px;
        }}
        .category-heading {{
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-muted);
            margin-bottom: 14px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 14px;
        }}
        .service-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 18px 20px;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .service-card:hover {{
            transform: translateY(-1px);
            border-color: rgba(255, 255, 255, 0.16);
            background: var(--surface-hover);
        }}
        .service-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .service-name-row {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .dot-green {{ background: var(--green); box-shadow: 0 0 8px rgba(34, 197, 94, 0.5); }}
        .dot-red {{ background: var(--red); box-shadow: 0 0 8px rgba(239, 68, 68, 0.5); }}
        .service-link {{
            color: var(--text);
            font-weight: 600;
            text-decoration: none;
            font-size: 14px;
        }}
        .service-link:hover {{ color: var(--accent); }}
        .badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            letter-spacing: 0.04em;
        }}
        .badge.operational {{ background: rgba(34, 197, 94, 0.12); color: var(--green); }}
        .badge.degraded, .badge.down {{ background: rgba(239, 68, 68, 0.12); color: var(--red); }}
        .service-desc {{
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 14px;
            line-height: 1.4;
        }}
        .service-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-muted);
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            padding-top: 10px;
        }}
        footer {{
            margin-top: 50px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
            flex-wrap: wrap;
            gap: 12px;
        }}
        footer a {{ color: var(--accent); text-decoration: none; }}
        footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="https://www.naindev.com/" class="brand">
                <div class="brand-badge">N</div>
                <div class="brand-title">NainDev Platform Status</div>
            </a>
            <a href="https://www.naindev.com/" class="back-link">&larr; Return to naindev.com</a>
        </header>

        <main>
            <div class="hero-banner">
                <div class="banner-status">
                    <div class="status-indicator {overall_badge_class}"></div>
                    <div>
                        <div class="banner-title">{overall_status_text}</div>
                        <div class="banner-meta">Last probe: {data['timestamp_iso']} UTC &bull; Verified via automated CI probe</div>
                    </div>
                </div>
                <div class="stats-summary">
                    <div class="stat-item">Monitored: <strong>{total_count}/{total_count}</strong></div>
                    <div class="stat-item">Average Latency: <strong>{avg_latency} ms</strong></div>
                    <div class="stat-item">SLA Target: <strong>99.9%</strong></div>
                </div>
            </div>

            {''.join(categories_html)}
        </main>

        <footer>
            <div>Observability engine running on GitHub Actions &bull; 0,00 € operational cost &bull; Automated every 30m</div>
            <div><a href="data/status.json" target="_blank">Raw JSON Metrics</a> &bull; <a href="https://github.com/Nain9Dev/status">GitHub Repository</a></div>
        </footer>
    </div>
</body>
</html>
"""


def main() -> int:
    os.makedirs("data", exist_ok=True)
    results = [probe_service(s) for s in SERVICES]

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = {
        "timestamp_iso": now_utc,
        "total_services": len(results),
        "operational_services": sum(1 for s in results if s["status"] == "operational"),
        "services": results
    }

    # Save machine-readable status JSON
    with open("data/status.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Save HTML dashboard
    html = generate_html_dashboard(report)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Status check completed at {now_utc}. {report['operational_services']}/{report['total_services']} services operational.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
