.PHONY: build run test lint format clean help test-api test-root test-health test-tools test-execute test-execute-zones test-execute-policies isort black pre-commit pre-commit-install security-scan checkov gitleaks

SHELL := /bin/bash
PROJECT_NAME := panos-mcp
DOCKER_IMAGE := ghcr.io/cdot65/$(PROJECT_NAME)
VERSION := latest
SERVICE_IP := $(shell kubectl get service -n panos panos-mcp-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

help:  ## Show help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build:  ## Build the docker image for multi-architecture
	docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_IMAGE):$(VERSION) -f docker/Dockerfile .

push:  ## Push the docker image to the registry
	docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_IMAGE):$(VERSION) -f docker/Dockerfile . --push

run:  ## Run the FastAPI server locally
	poetry run uvicorn src.panos_mcp.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	poetry run python -m pytest

lint:  ## Run linting checks
	poetry run flake8 src

format:  ## Format code using ruff
	poetry run ruff format src

isort:  ## Sort imports using isort
	poetry run isort src

black:  ## Format code using black
	poetry run black src

pre-commit:  ## Run pre-commit on all files
	poetry run pre-commit run --all-files

pre-commit-install:  ## Install pre-commit hooks
	poetry run pre-commit install

security-scan: checkov gitleaks  ## Run all security scanning tools

checkov:  ## Run Checkov security scans
	poetry run checkov --directory . --quiet

gitleaks:  ## Run GitLeaks to detect secrets
	@command -v gitleaks >/dev/null 2>&1 || { echo >&2 "gitleaks is not installed. Install it with 'brew install gitleaks'"; exit 1; }
	gitleaks detect --source . --verbose

clean:  ## Clean build artifacts
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf dist
	rm -rf build

install:  ## Install dependencies
	poetry install

update:  ## Update dependencies
	poetry update

deploy:  ## Deploy to Kubernetes
	kubectl apply -f k8s/

dev-env:  ## Setup development environment
	poetry install
	$(MAKE) pre-commit-install

# API Testing targets

test-api: test-root test-health test-tools test-execute test-execute-zones test-execute-policies  ## Test all API endpoints

test-root:  ## Test the root endpoint
	@echo "Testing root endpoint..."
	@curl -s http://$(SERVICE_IP)/ | jq

test-health:  ## Test the health endpoint
	@echo "Testing health endpoint..."
	@curl -s http://$(SERVICE_IP)/health | jq

test-tools:  ## Test the tools endpoint
	@echo "Testing tools endpoint..."
	@curl -s http://$(SERVICE_IP)/mcp/tools | jq

test-execute:  ## Test the execute endpoint with retrieve_address_objects
	@echo "Testing execute endpoint with retrieve_address_objects..."
	@curl -s -X POST http://$(SERVICE_IP)/mcp/execute \
		-H "Content-Type: application/json" \
		-d '{"tool": "retrieve_address_objects", "parameters": {"location": "vsys", "vsys": "vsys1"}}' | jq

test-execute-zones:  ## Test the execute endpoint with retrieve_security_zones
	@echo "Testing execute endpoint with retrieve_security_zones..."
	@curl -s -X POST http://$(SERVICE_IP)/mcp/execute \
		-H "Content-Type: application/json" \
		-d '{"tool": "retrieve_security_zones", "parameters": {"location": "vsys", "vsys": "vsys1"}}' | jq

test-execute-policies:  ## Test the execute endpoint with retrieve_security_policies
	@echo "Testing execute endpoint with retrieve_security_policies..."
	@curl -s -X POST http://$(SERVICE_IP)/mcp/execute \
		-H "Content-Type: application/json" \
		-d '{"tool": "retrieve_security_policies", "parameters": {"location": "vsys", "vsys": "vsys1"}}' | jq
