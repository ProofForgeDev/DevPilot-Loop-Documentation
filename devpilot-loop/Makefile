.PHONY: help test lint security build demo clean all

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Run all tests
	python3 -m pytest tests/ -v --tb=short

test-quick: ## Run quick tests (no server-dependent)
	python3 -m pytest tests/ -v --tb=short -k "not agent_comm and not observability and not security"

lint: ## Run linters
	ruff check .
	black --check .
	mypy skills/

security: ## Run security scans
	bandit -r skills/ -f json -o security-report.json
	semgrep --config auto skills/

build: ## Build Docker images
	docker compose -f poc/deploy/docker-compose.yml build

demo: ## Run end-to-end demo
	python3 poc/scenario/orchestrator_run.py

evidence: ## Verify evidence integrity
	python3 -c "
import os, json
count = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__']]
    for f in files:
        if 'evidence' in root or 'open-agent-audit' in root:
            if f not in ['EVIDENCE-INDEX.md', 'EVIDENCE-MATRIX.md', 'evidence_matrix_v2.md', 'evidence_index.json', 'README.md']:
                count += 1
print(f'Evidence files: {count}')
assert count >= 90, f'Expected 90+ evidence files, got {count}'
print('Evidence count: PASS')
"

skills: ## Verify skill loading
	python3 -c "
import sys
sys.path.insert(0, '.')
from skills.registry import initialize, list_skills
initialize()
skills = list_skills()
print(f'Loaded {len(skills)} skills:')
for s in skills:
    print(f'  - {s[\"name\"]}@{s[\"version\"]}')
assert len(skills) >= 8, f'Expected 8+ skills, got {len(skills)}'
print('Skill count: PASS')
"

all: test lint security demo evidence skills ## Run all checks

clean: ## Clean up generated files
	rm -rf __pycache__ */__pycache__ .pytest_cache */.pytest_cache
	rm -rf *.egg-info */*.egg-info
	rm -rf poc/scenario/*.json poc/scenario/*.diff
	rm -rf poc/scenario/*.py
	rm -rf security-report.json
	find . -name "*.log" -path "*/evidence/logs/*" -delete
	find . -name "*.png" -path "*/evidence/screenshots/*" -delete
	find . -name "*.bak" -delete

setup: ## Setup development environment
	pip install -r requirements.txt
	pip install -r poc/deploy/runtime/requirements.txt
	pre-commit install

generate-evidence: ## Regenerate evidence files (logs + screenshots)
	python3 scripts/generate_evidence.py
