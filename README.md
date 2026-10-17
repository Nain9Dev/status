# NainDev Platform Status

<div align="center">

[![Uptime Probe](https://github.com/Nain9Dev/status/actions/workflows/uptime.yml/badge.svg)](https://github.com/Nain9Dev/status/actions/workflows/uptime.yml)
[![Live Status](https://img.shields.io/badge/status-100%25%20operational-success)](https://status.naindev.com/)
[![Engineering Handbook](https://img.shields.io/badge/paved%20road-Observability-blue)](https://github.com/Nain9Dev/engineering-handbook)
[![Cost](https://img.shields.io/badge/cost-0.00_%E2%82%AC-22c55e)](https://github.com/Nain9Dev/engineering-handbook/blob/main/governance/zero-cost-philosophy.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational)](LICENSE)

</div>

Real-time uptime, response latency, and operational health metrics across all NainDev platforms, services, and showcase applications.

Live dashboard: [https://status.naindev.com/](https://status.naindev.com/)

## Architecture

- **Probe Engine**: Deterministic Python runner (`scripts/monitor.py`) executing concurrent HTTP requests (`ThreadPoolExecutor`) with automated retries against all portfolio microservices and web applications.
- **Resilience**: Dual-attempt probes filter out transient network blips and prevent false positives.
- **Automation**: GitHub Actions workflow (`.github/workflows/uptime.yml`) executing on a 30-minute cron cadence and on manual triggers (`workflow_dispatch`).
- **Keepalive**: Automated workflow keepalive prevents GitHub from pausing scheduled cron jobs after 60 days of inactivity.
- **Storage**: Flat-file JSON metrics (`data/status.json`) and rolling historical summaries (`data/history.json`) for verifiable measured uptime calculation without database overhead.
- **Hosting**: Static edge delivery via GitHub Pages with custom CNAME proxying through Cloudflare at 0.00 € operational expense.

## Monitored Services

| Category | Service | Target URL |
|---|---|---|
| Platform Hub | NainDev Portfolio | `https://www.naindev.com/` |
| Platform Hub | NainDev Brandbook | `https://brand.naindev.com/` |
| Backend & Cloud | NainPolicy (.NET 10) | `https://policy.naindev.com/` |
| Backend & Cloud | NainOrder (.NET 10) | `https://order.naindev.com/` |
| Backend & Cloud | NainDrive (FastAPI) | `https://drive.naindev.com/` |
| Backend & Cloud | NainNotify (.NET 10) | `https://notify.naindev.com/` |
| Backend & Cloud | NainTAI (.NET 10) | `https://tai.naindev.com/` |
| Backend & Cloud | TAI Study System (Vercel) | `https://tai-study-system-js.vercel.app/` |
| 3D & Conformance | Nain3D Gateway | `https://3d.naindev.com/` |
| 3D & Conformance | ParametriCAD AI | `https://parametricad.naindev.com/` |
| 3D & Conformance | NainConfigurator | `https://configurator.naindev.com/` |
| Workbenches | NainProspect | `https://prospect.naindev.com/` |
| Workbenches | NainWrite | `https://write.naindev.com/` |
| Workbenches | HaveTickets | `https://tickets.naindev.com/` |
| Workbenches | GameHaven | `https://gamehaven.naindev.com/` |
| Games (Zero Engine) | Orbe3D | `https://orbe.naindev.com/` |
| Games (Zero Engine) | PongArcade | `https://pong.naindev.com/` |

## Local Development & Testing

```bash
# Run unit test suite
python -m unittest discover -s tests -v

# Run local probe and generate dashboard
python scripts/monitor.py
```

## License

This project is licensed under the [MIT License](LICENSE).
