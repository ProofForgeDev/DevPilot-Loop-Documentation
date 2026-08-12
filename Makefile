#!/bin/bash
# DevPilot Loop - Makefile for development workflow
# =================================================

PYTHON := python3
PIP := pip3
DOCKER := docker
COMPOSE := docker compose

.PHONY: help install dev prod test clean docker-up docker-down \
        lint format docs slides evidence reset deploy status

## help: Show this help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

## install: Install all dependencies
install:
	@echo "Installing dependencies..."
	$(PIP) install --break-system-packages -e "skills[dev]" 2>/dev/null || \
	$(PIP) install -e "skills[dev]"
	$(PIP) install --break-system-packages -r poc/scenario/requirements.txt 2>/dev/null || true

## dev: Start development servers (local, no Docker)
dev:
	@echo "Starting DevPilot Loop in development mode..."
	AGENT_NAME=devlead AGENT_TYPE=manager PORT=8008 $(PYTHON) poc/deploy/runtime/agent_runtime.py &
	AGENT_NAME=intake AGENT_TYPE=worker SKILL_NAME=triage PORT=8001 $(PYTHON) poc/deploy/runtime/agent_runtime.py &
	AGENT_NAME=analyst AGENT_TYPE=worker SKILL_NAME=root-cause PORT=8002 $(PYTHON) poc/deploy/runtime/agent_runtime.py &
	AGENT_NAME=fixer AGENT_TYPE=worker SKILL_NAME=patch PORT=8003 $(PYTHON) poc/deploy/runtime/agent_runtime.py &
	AGENT_NAME=verifier AGENT_TYPE=worker SKILL_NAME=test PORT=8004 $(PYTHON) poc/deploy/runtime/agent_runtime.py &
	AGENT_NAME=release AGENT_TYPE=worker SKILL_NAME=deploy PORT=8005 $(PYTHON) poc/deploy/runtime/agent_runtime.py &
	AGENT_NAME=knowledge AGENT_TYPE=worker SKILL_NAME=doc PORT=8006 $(PYTHON) poc/deploy/runtime/agent_runtime.py &
	@echo "Servers started. Ports: 8001-8006 (workers), 8008 (manager)"

## prod: Start production via Docker Compose
prod: docker-up

## docker-up: Start all services with Docker
docker-up:
	@echo "Starting DevPilot Loop with Docker Compose..."
	$(COMPOSE) up -d
	@echo "Services started. Check status with: make status"

## docker-down: Stop all Docker services
docker-down:
	@echo "Stopping all Docker services..."
	$(COMPOSE) down

## docker-status: Show service status
docker-status:
	$(COMPOSE) ps

## test: Run all tests
test:
	@echo "Running test suite..."
	$(PYTHON) -m pytest tests/ -v --tb=short

## test-skills: Run skill tests only
test-skills:
	@echo "Running skill validation tests..."
	$(PYTHON) tests/test_skills_validation.py

## test-comm: Run communication tests
test-comm:
	@echo "Running agent communication tests..."
	$(PYTHON) tests/test_agent_comm.py

## lint: Run linting
lint:
	@echo "Running linter..."
	$(PYTHON) -m py_compile poc/deploy/runtime/agent_runtime.py
	$(PYTHON) -m py_compile skills/base.py
	$(PYTHON) -m py_compile skills/registry.py

## format: Format code
format:
	@echo "Formatting code..."
	$(PYTHON) -m autopep8 --in-place --recursive skills/ poc/

## docs: Generate documentation
docs:
	@echo "Generating documentation..."
	$(PYTHON) docs/generate_docs.py 2>/dev/null || echo "Docs generator not available"

## slides: Generate presentation
slides:
	@echo "Generating slides..."
	cd slides && $(PYTHON) generate_ppt.py

## evidence: Generate evidence files
evidence:
	@echo "Generating evidence screenshots..."
	cd poc/evidence && $(PYTHON) generate_screenshots.py 2>/dev/null || true

## reset: Clean and restart everything
reset: docker-down docker-up
	@echo "DevPilot Loop reset complete!"

## status: Show system status
status:
	@echo "=== Service Status ==="
	@curl -s http://localhost:8008/health 2>/dev/null || echo "Manager: DOWN"
	@curl -s http://localhost:8001/health 2>/dev/null || echo "Intake: DOWN"
	@curl -s http://localhost:8002/health 2>/dev/null || echo "Analyst: DOWN"
	@curl -s http://localhost:8003/health 2>/dev/null || echo "Fixer: DOWN"
	@curl -s http://localhost:8004/health 2>/dev/null || echo "Verifier: DOWN"
	@curl -s http://localhost:8005/health 2>/dev/null || echo "Release: DOWN"
	@curl -s http://localhost:8006/health 2>/dev/null || echo "Knowledge: DOWN"
	@echo "=== Test Status ==="
	@$(PYTHON) -m pytest tests/ --tb=no -q 2>/dev/null || echo "Tests: FAIL (pytest not installed)"

## deploy: Deploy to production
deploy:
	@echo "Deploying to production..."
	$(COMPOSE) -f docker-compose.prod.yml up -d
	@echo "Deployment complete!"

## benchmark: Run performance benchmark
benchmark:
	@echo "Running benchmarks..."
	$(PYTHON) scripts/benchmark.py 2>/dev/null || echo "Benchmark script not available"

## clean: Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf dist/
	rm -rf build/
	find . -name "*.pyc" -delete

## logs: View service logs
logs:
	$(COMPOSE) logs -f

## shell: Open shell in container
shell:
	$(COMPOSE) exec devlead bash

.DEFAULT_GOAL := help
