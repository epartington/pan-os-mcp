.PHONY: build run test lint format clean help test-sse isort black pre-commit pre-commit-install security-scan checkov gitleaks setup-buildx build-multi push-multi

SHELL := /bin/bash
PROJECT_NAME := panos-mcp
DOCKER_IMAGE := ghcr.io/cdot65/$(PROJECT_NAME)
VERSION := latest
NAMESPACE := panos-mcp-service

help:  ## Show help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup-buildx:  ## Setup Docker buildx for multi-architecture builds
	docker buildx create --name multiarch --use || true
	docker buildx inspect --bootstrap

build:  ## Build the docker image for amd64 architecture (even on Apple Silicon)
	docker buildx build --platform linux/amd64 --load -t $(DOCKER_IMAGE):$(VERSION) .

build-multi:  ## Build the docker image for multiple architectures
	docker buildx build --builder multiarch --platform linux/amd64,linux/arm64 -t $(DOCKER_IMAGE):$(VERSION) .

push:  ## Push the docker image to the registry (amd64 only)
	docker buildx build --platform linux/amd64 -t $(DOCKER_IMAGE):$(VERSION) . --push

push-multi:  ## Push multi-architecture docker image to the registry
	docker buildx build --builder multiarch --platform linux/amd64,linux/arm64 -t $(DOCKER_IMAGE):$(VERSION) . --push

run:  ## Run the MCP server locally
	python src/main.py

test:  ## Run tests
	poetry run python -m pytest

test-sse:  ## Test the SSE endpoint
	curl -v http://localhost:8000/messages/

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
	pip install -r requirements.txt

update:  ## Update dependencies
	pip install -U -r requirements.txt

deploy:  ## Deploy to Kubernetes
	kubectl apply -f k8s/

status:  ## Check deployment status
	kubectl get pods -n $(NAMESPACE)

logs:  ## View pod logs
	@POD=$$(kubectl get pods -n $(NAMESPACE) -l app=panos-mcp -o jsonpath='{.items[0].metadata.name}'); \
	kubectl logs -f $$POD -n $(NAMESPACE)

delete:  ## Delete deployment
	kubectl delete -f k8s/

dev-env:  ## Setup development environment
	pip install -r requirements.txt
