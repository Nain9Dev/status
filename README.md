# NainDev Platform Status

Real-time uptime, response latency, and operational health metrics across all NainDev platforms, services, and showcase applications.

Live dashboard: [https://status.naindev.com/](https://status.naindev.com/)

## Architecture

- **Probe Engine**: Deterministic Python runner (`scripts/monitor.py`) executing concurrent HTTP requests against all portfolio microservices and web applications.
- **Automation**: GitHub Actions workflow (`.github/workflows/uptime.yml`) executing on a 30-minute cron cadence and on manual triggers (`workflow_dispatch`).
- **Storage**: Flat-file JSON metrics (`data/status.json`) committed directly to Git, enabling zero-database persistence and cost-free historical tracking.
- **Hosting**: Static edge delivery via GitHub Pages with custom CNAME proxying through Cloudflare at 0.00 € operational expense.

## Monitored Services

| Category | Service | Target URL |
|---|---|---|
| Platform Hub | NainDev Portfolio | `https://www.naindev.com/` |
| Backend & Cloud | NainPolicy (.NET 10) | `https://policy.naindev.com/` |
| Backend & Cloud | NainOrder (.NET 10) | `https://order.naindev.com/` |
| Backend & Cloud | NainDrive (FastAPI) | `https://drive.naindev.com/` |
| Backend & Cloud | NainNotify (.NET 10) | `https://notify.naindev.com/` |
| Backend & Cloud | NainTAI (.NET 10) | `https://tai.naindev.com/` |
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
# Run test suite
python -m unittest discover -s tests -v

# Run local probe and generate dashboard
python scripts/monitor.py
```
