# Windows-compatible Makefile for Home Threat Detection
# Detects OS and uses appropriate commands

ifeq ($(OS),Windows_NT)
    SHELL := powershell.exe
    .SHELLFLAGS := -NoProfile -Command
    RM = Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    MKDIR = New-Item -ItemType Directory -Force -Path
    PYTHON = python
else
    SHELL := /bin/bash
    RM = rm -rf
    MKDIR = mkdir -p
    PYTHON = python3
endif

.PHONY: install playground backend local-backend setup-dev-env test lint clean demo

# Install dependencies using uv package manager
install:
ifeq ($(OS),Windows_NT)
	@echo "Checking for uv installation..."
	@powershell -Command "if (!(Get-Command uv -ErrorAction SilentlyContinue)) { Write-Host 'Installing uv...'; irm https://astral.sh/uv/0.6.12/install.ps1 | iex }"
	uv sync --dev
else
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; }
	uv sync --dev
endif
	@echo "✓ Dependencies installed"

# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting threat detection playground...                                  |"
	@echo "|                                                                             |"
	@echo "| 💡 Try simulating different threat scenarios                                |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# Deploy the agent remotely to Cloud Run
backend:
ifeq ($(OS),Windows_NT)
	@powershell -Command "$$PROJECT_ID = (gcloud config get-value project); gcloud beta run deploy home-threat-detection --source . --memory '4Gi' --project $$PROJECT_ID --region 'us-central1' --no-allow-unauthenticated --no-cpu-throttling --labels 'created-by=adk' --set-env-vars 'COMMIT_SHA=$$(git rev-parse HEAD)' $(if $(IAP),--iap) $(if $(PORT),--port=$(PORT))"
else
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy home-threat-detection \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk" \
		--set-env-vars "COMMIT_SHA=$$(git rev-parse HEAD)" \
		$(if $(IAP),--iap) \
		$(if $(PORT),--port=$(PORT))
endif

# Launch local development server with hot-reload
local-backend:
	@echo "Starting local backend on http://localhost:8000"
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

# Run the demo pipeline
demo:
	@echo "Running threat detection demo..."
	uv run python -m app.pipeline

# Run demo with specific scenario
demo-intrusion:
	@echo "Running INTRUSION scenario..."
	uv run python -c "import asyncio; from app.pipeline import ThreatDetectionPipeline; asyncio.run(ThreatDetectionPipeline({}, 'intrusion').process_cycle())"

demo-fall:
	@echo "Running FALL scenario..."
	uv run python -c "import asyncio; from app.pipeline import ThreatDetectionPipeline; asyncio.run(ThreatDetectionPipeline({}, 'fall').process_cycle())"

demo-fire:
	@echo "Running FIRE scenario..."
	uv run python -c "import asyncio; from app.pipeline import ThreatDetectionPipeline; asyncio.run(ThreatDetectionPipeline({}, 'fire').process_cycle())"

# Set up development environment resources using Terraform
setup-dev-env:
ifeq ($(OS),Windows_NT)
	@powershell -Command "$$PROJECT_ID = (gcloud config get-value project); cd deployment/terraform/dev; terraform init; terraform apply -var-file=vars/env.tfvars -var=dev_project_id=$$PROJECT_ID -auto-approve"
else
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)
endif

# Run unit and integration tests
test:
	@echo "Running tests..."
	uv run pytest tests/unit -v
	uv run pytest tests/integration -v

# Run code quality checks
lint:
	@echo "Running code quality checks..."
	uv sync --dev --extra lint
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy app/

# Clean build artifacts
clean:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, *.egg-info, dist, build"
else
	$(RM) __pycache__ .pytest_cache .mypy_cache .ruff_cache *.egg-info dist build
endif
	@echo "✓ Cleaned build artifacts"

# Show help
help:
	@echo "Home Threat Detection System - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        - Install all dependencies"
	@echo "  make setup-dev-env  - Setup GCP development environment"
	@echo ""
	@echo "Development:"
	@echo "  make playground     - Launch ADK web playground"
	@echo "  make local-backend  - Run local server on port 8000"
	@echo "  make demo           - Run full demo pipeline"
	@echo "  make demo-intrusion - Run intrusion scenario"
	@echo "  make demo-fall      - Run fall detection scenario"
	@echo "  make demo-fire      - Run fire detection scenario"
	@echo ""
	@echo "Deployment:"
	@echo "  make backend        - Deploy to Cloud Run"
	@echo "  make backend IAP=true - Deploy with IAP enabled"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run code quality checks"
	@echo "  make clean          - Clean build artifacts"
	@echo ""

# Default target
.DEFAULT_GOAL := help