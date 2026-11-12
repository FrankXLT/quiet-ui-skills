# Icons (primitive)

A monochrome 24×24 vector icon library for architecture, data-flow, sequence, and systems diagrams. Each icon uses `currentColor` so it inherits ink from its parent SVG and adapts to Quiet UI's 4-theme tokens (`white`, `paper`, `dark-paper`, `dark`).

## Usage

Copy the fenced `<svg>` snippet into your diagram, or reference icons via `<use href="assets/icons-<type>.svg#icon-<name>"/>`. Default size is 24×24; wrap in `<g transform="translate(x,y) scale(s)">` to position and resize.

Generic icons are stroked (1.5px hairline); brand silhouettes are filled. Don't mix styles unnecessarily in the same diagram.

## Icon Catalog Overview

Icons are divided across three focused reference files:
- **General IT & Systems:** [icons-general.md](icons-general.md) — Compute (laptop, server, vm), People (user, admin), Network (cloud, firewall, gateway, dns), and Actions (api, request, response, sync, lock, key, alert).
- **Cloud & Infrastructure:** [icons-cloud.md](icons-cloud.md) — Kubernetes (pod, node, service, ingress), DevOps (git, pipeline, test), Storage (data, queue, bucket), and Cloud Providers (AWS, Azure, GCP, Terraform, Docker, GitHub, Keycloak, Active Directory, MinIO).
- **Tech Stack & Databases:** [icons-tech.md](icons-tech.md) — PostgreSQL, MySQL, Redis, SQLite, Kafka, RabbitMQ, Data Pipeline Tools (NiFi, Airflow, Trino, Superset, Jupyter), Languages (Python, R, SQL), and Formats.

### SVG Sheet Assets
Pre-compiled symbol sheets are available in `assets/`:
- `assets/icons-general.svg`
- `assets/icons-cloud.svg`
- `assets/icons-tech.svg`

### Open Source Attribution
- Stroked icons: Tabler Icons (MIT License)
- Brand silhouettes: Simple Icons (CC0 / Open Source)
- Devicon (MIT License)
- `log-z/logos` (MIT License)
