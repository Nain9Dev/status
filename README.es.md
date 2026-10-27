# Estado de la plataforma NainDev

<div align="center">

[![Language: English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Versión en Español](https://img.shields.io/badge/Versión-Español-red.svg)](#)
[![Sonda de disponibilidad](https://github.com/Nain9Dev/status/actions/workflows/uptime.yml/badge.svg)](https://github.com/Nain9Dev/status/actions/workflows/uptime.yml)
[![Estado en vivo](https://img.shields.io/badge/status-100%25%20operativo-success)](https://status.naindev.com/)
[![Engineering Handbook](https://img.shields.io/badge/paved%20road-Observability-blue)](https://github.com/Nain9Dev/engineering-handbook)
[![Coste](https://img.shields.io/badge/cost-0.00_%E2%82%AC-22c55e)](https://github.com/Nain9Dev/engineering-handbook/blob/main/governance/zero-cost-philosophy.md)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-informational)](LICENSE)

</div>

Métricas en tiempo real de disponibilidad, latencia de respuesta y salud operativa de todas las plataformas, servicios y aplicaciones del ecosistema NainDev.

Panel en directo: [https://status.naindev.com/](https://status.naindev.com/)

## Arquitectura

- **Motor de sondas**: Ejecutor determinista en Python (`scripts/monitor.py`) que realiza peticiones HTTP concurrentes (`ThreadPoolExecutor`) con reintentos automáticos contra todos los microservicios y aplicaciones web del portfolio.
- **Resiliencia**: Sondas de doble intento para filtrar caídas transitorias de red y evitar falsos positivos.
- **Automatización**: Flujo de GitHub Actions (`.github/workflows/uptime.yml`) ejecutado en cadencia cron cada 30 minutos y mediante activadores manuales (`workflow_dispatch`).
- **Persistencia**: Keepalive automatizado que evita que GitHub pause tareas cron programadas tras 60 días de inactividad.
- **Almacenamiento**: Métricas JSON en archivos planos (`data/status.json`) y resúmenes históricos acumulativos (`data/history.json`) para el cálculo verificable del tiempo de actividad sin sobrecarga de base de datos.
- **Alojamiento**: Entrega estática en el borde mediante GitHub Pages con CNAME personalizado enrutado a través de Cloudflare a un coste operativo de 0,00 €.

## Servicios monitorizados

| Categoría | Servicio | URL objetivo |
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
| Juegos (Zero Engine) | Orbe3D | `https://orbe.naindev.com/` |
| Juegos (Zero Engine) | PongArcade | `https://pong.naindev.com/` |

## Desarrollo local y pruebas

```bash
# Ejecutar suite de pruebas unitarias
python -m unittest discover -s tests -v

# Ejecutar sonda local y generar panel
python scripts/monitor.py
```

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).
