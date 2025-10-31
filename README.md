# NEXA — Next‑gen Project Intelligence

Real-time AI assistant unifying Jira, GitHub, and MS Teams to predict risks, optimize resources, and automate compliance.

Summary
NEXA (Next‑gen Project Intelligence) is an AI-powered project management assistant built to give automotive software teams real-time visibility across tools (Jira, GitHub, MS Teams), predict risks and delays, and optimize resource allocation while helping automate compliance (ISO 26262 / ASPICE) and reporting.

Why this project
Automotive software development is complex and highly regulated. Project managers spend a large portion of their time manually consolidating data from multiple tools, which delays actionable insights and increases risk. NEXA automates data consolidation, delivers predictive insights, and provides natural-language summaries so teams can act proactively.

Problem statement
• Data fragmentation across Jira, GitHub, and communication platforms makes real-time decision-making difficult.
• Project managers waste time manually consolidating data.
• Resource bottlenecks and risks are often detected too late.
• Compliance preparation is slow and manual.

Goals & success criteria
• Unified dashboards with up-to-date metrics across tools (progress, backlog, velocity, PRs/issues).
• Resource allocation view showing workload distribution and hotspots.
• Risk prediction engine that surfaces probable delays and their drivers.
• AI-generated daily/weekly summaries for managers and stakeholders.

Expected impact
• Reduced reporting overhead (target: ~50% less manual effort).
• Faster risk detection and earlier mitigation.
• Better resource utilization and balanced workload.
• Faster audit preparation and compliance traceability.

Hackathon & team
Acsia Hackathon 2025 — Team Submission
Category: PS02 – AI/ML for Automotive Software Development
Team: Priti Gupta, Avishek Rauniyar

Project architecture (high level)
• Microservices: FastAPI services running in containers, deployed to Kubernetes for scale.
• Messaging/ingestion: Kafka for event streaming; Redis for caches and real-time signals.
• Storage: PostgreSQL for transactional data; object store for artifacts.
• ML: XGBoost/LSTM for risk prediction, GNN for resource optimization; models served via TF/PyTorch serving.
• Frontend: React + TypeScript, real-time via WebSocket.
• Observability: Prometheus, Grafana, and ELK stack.

Key components
• Data Integrator — connectors for Jira, GitHub, Teams (sync, webhooks, rate-limit-aware ingestion).
• Dashboard Service — aggregates metrics and serves the UI.
• Resource Optimizer — ML microservice for workload balancing.
• Risk Engine — prediction microservice with explainability (SHAP).
• Summarizer — GPT-powered natural-language reports and voice interface.

Quick start (developer MVP)
Prerequisites
• Docker & Docker Compose
• Node 18+ (frontend) and Python 3.10+ (backend) — optional locally if running services without containers

Local dev (MVP using Docker Compose)
1. Clone the repo
	git clone <repo-url>
	cd NextGen-Project-AI
2. Copy example envs and update credentials for integrations
	cp .env.example .env
	# Edit .env to add API keys for Jira/GitHub/Teams or set dummy values for local dev
3. Start services
	docker compose up --build

Notes
• The repository contains the project kickoff docs and high-level artifacts for the Hackathon MVP. Implementation scaffolding (microservices, infra manifests) should be added under logical folders (backend/, frontend/, infra/).
• For secure integrations, use secret stores (Azure Key Vault / Kubernetes secrets) in production.

How to contribute
Please read `CONTRIBUTING.md` for branch/PR rules, code style, and testing expectations. Also read `CODE_OF_CONDUCT.md`.

Roadmap (short)
1. Create connector templates for Jira and GitHub (webhooks + incremental sync).
2. Implement a minimal dashboard service and sample frontend showing issues/PRs.
3. Build a simple risk predictor using historical issue/PR velocity and test predictions.
4. Add automated compliance report skeleton (traceability matrix generator).

Contact
For questions about the project or hackathon submission, reach out to the team leads in the repo or open an issue.

License
Specify a license for the repository (e.g., Apache-2.0) — add `LICENSE` file.

A full-stack AI-powered project management assistant that integrates with Jira, GitHub, and Slack/Rocket.Chat to automate project dashboards, monitor team resource allocation, predict delivery risks, and generate natural-language status reports for managers and stakeholders.  
