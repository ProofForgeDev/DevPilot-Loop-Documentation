---
name: run-devpilot-loop
description: Use when running, testing, or debugging DevPilot Loop — the multi-agent autonomous R&D system. Triggers on: "run devpilot", "start devpilot", "run the e2e demo", "check devpilot services", "run skill tests", "generate ppt", "check evidence", "show devpilot status". Also use when asked to launch the HiClaw-compatible runtime, verify Docker services, or drive the end-to-end scenario.
---

# DevPilot Loop — Run Skill

## Overview

DevPilot Loop is a multi-agent autonomous closed-loop system for software R&D, built on AgentTeams (HiClaw). It runs 8 Docker services (1 Manager + 6 Workers + 1 Gateway) and provides 6 installable Python skills. This skill lets you launch, verify, and drive the entire project from a clean machine.

**Agent path:** All interactions go through `.claude/skills/run-devpilot-loop/driver.py`. It wraps Docker Compose, curl health checks, pytest, the e2e scenario demo, and PPT generation.

## Prerequisites

```bash
# macOS (Homebrew)
brew install docker docker-compose

# Linux (Ubuntu)
sudo apt-get update && sudo apt-get install -y docker.io docker-compose

# Verify
docker --version && docker compose version
python3 --version  # 3.10+
pip3 install poetry || true  # optional, project uses .venv
```

## Setup (one-time)

```bash
cd /path/to/devpilot-loop
python3 -m venv .venv
.venv/bin/pip install -q fastapi uvicorn httpx pyyaml pytest python-pptx pillow
```

## Run (Agent Path)

All commands below are run from the project root:

```bash
DRIVER=".claude/skills/run-devpilot-loop/driver.py"
VENV=".venv/bin/python"
```

### 1. Start Services

```bash
$VENV $DRIVER compose-up
```

This runs `docker compose up -d` in `poc/deploy/` and waits 15s for all 8 services to become healthy.

### 2. Check Status

```bash
# Quick health check (curl to all 8 endpoints)
$VENV $DRIVER health

# Or detailed container view
$VENV $DRIVER compose-status
```

Expected output: `8 healthy` (all green).

### 3. Run End-to-End Demo

```bash
$VENV $DRIVER e2e
```

Runs `poc/scenario/e2e_demo.py` — 6 steps (Intake → Analyst → Fixer → Verifier → Release → Knowledge) against the Flask login-module-with-bugs scenario. Outputs saved to `poc/scenario/`.

### 4. Run Skill Tests

```bash
$VENV $DRIVER skills-test
```

Installs all 6 skill packages, runs registry verification, executes 29 pytest tests.*?274 passed`.

### 5. Run Pytest Suite

```bash
$VENV $DRIVER tests
```

Runs `tests/test_agent_comm.py`. Note: these tests require the Docker services to be running and use function-style fixtures that may error — the e2e demo and skills-test are the primary validation paths.

### 6. Generate PPT

```bash
$VENV $DRIVER ppt
```

Generates `slides/DevPilot_Loop_preliminary.pptx` (36 pages, 8 chapters).

### 7. Evidence & Manifest

```bash
$VENV $DRIVER evidence        # List all evidence files
$VENV $DRIVER manifest        # Show last e2e task manifest
$VENV $DRIVER screenshot     # Generate headless screenshot report
```

### 8. Stop Services

```bash
$VENV $DRIVER compose-down
```

## Direct API Interaction (curl)

For manual probing, all agents expose standard HTTP:

```bash
# Health of any service
curl http://localhost:8001/health   # Intake
curl http://localhost:8008/health   # Manager

# Dispatch a task to Manager
curl -X POST http://localhost:8008/dispatch \
  -H "Content-Type: application/json" \
  -d '{"task_id":"DEMO-001","source":"manual","raw_payload":{"issue":"login bug"},"priority":"P1"}'

# List tasks from Manager
curl http://localhost:8008/tasks
```

## Gotchas

- **Docker must be running first.** If `docker ps` shows nothing, start Docker Desktop or `systemctl start docker`.
- **Ports 8001-8008 must be free.** `lsof -i :8001-8008` to check.
- **Tests require services up.** `tests/test_agent_comm.py` curls localhost directly — won't work if Docker isn't running.
- **Skills need .venv.** The project virtualenv is at `.venv/`; don't use system Python.
- **Evidence screenshots are text placeholders.** `poc/evidence/screenshots/*.png` are placeholder files with embedded metadata — not real PNGs. The `screenshot` driver command generates a text report instead.
- **Compose context is `poc/`, not project root.** The Dockerfile COPY paths are relative to `poc/`. Always run compose from project root (the compose file handles this via `context: ..`).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `docker: compose not found` | Install `docker-compose-plugin` or use `docker-compose` (v1) |
| `Connection refused` on health check | Services not running yet — run `driver.py compose-up` and wait 15s |
| `port already in use` | Kill existing containers: `docker compose -f poc/deploy/docker-compose.yml down` then restart |
| `E fixture 'manager_url' not found` | Pre-existing test issue — use `e2e` and `skills-test` instead of `tests` |
| Skill install fails with `ModuleNotFoundError` | Activate venv: `source .venv/bin/activate` or use `.venv/bin/python` explicitly |
| PPT generation fails `RGBColor` import | Reinstall: `.venv/bin/pip install -q python-pptx pillow` |

## Files

```
.claude/skills/run-devpilot-loop/
  SKILL.md       ← you are reading this
  driver.py      ← all commands above (copy this path exactly)

poc/deploy/
  docker-compose.yml   # 8 services: gateway + manager + 6 workers
  runtime/agent_runtime.py  # FastAPI HiClaw-compatible runtime

poc/scenario/
  e2e_demo.py          # 6-step end-to-end demo
  login_module.py      # Flask app with 4 intentional bugs

skills/
  install_test.py      # 29-test validation script
  base.py              # BaseSkill ABC
  registry.py          # Auto-discovery registry

slides/
  generate_ppt.py      # python-pptx 36-page generator
```
