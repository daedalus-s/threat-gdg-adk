# Home Threat Detection System - Makefile

.PHONY: install playground backend local-backend test lint setup-dev-env

# Install dependencies using pip or uv
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $$HOME/.local/bin/env; }
	uv sync --dev

# Launch local development playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting threat detection system playground...                          |"
	@echo "|                                                                             |"
	@echo "| 💡 Open http://localhost:8501 to view the dashboard                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Make sure video files are in data/videos/                     |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# Launch local development server with hot-reload
local-backend:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

# Deploy to Cloud Run
backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud run deploy home-threat-detection \
		--source . \
		--memory "8Gi" \
		--cpu "4" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--set-env-vars="COMMIT_SHA=$$(git rev-parse HEAD)"

# Run tests
test:
	uv run pytest tests/unit
	uv run pytest tests/integration

# Run code quality checks
lint:
	uv sync --dev
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

# Set up development environment with Terraform
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform && terraform init && terraform apply --auto-approve)

# Run video frame extraction test
test-video:
	uv run python -m app.tools.video_processor --test

# Run sensor simulator test
test-sensors:
	uv run python -m app.simulators.sensor_simulator --test

# Start demo scenario
demo:
	@echo "Starting full threat detection demo..."
	uv run python scripts/run_demo.py