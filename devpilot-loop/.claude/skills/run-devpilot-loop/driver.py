#!/usr/bin/env python3
"""
DevPilot Loop — Agent Driver
=============================
Programmatic harness for driving the DevPilot Loop project.
Run this from the project root to interact with all subsystems.

Usage:
    python3 .claude/skills/run-devpilot-loop/driver.py <command> [args]

Commands:
    health          — Check all 8 running services
    compose-up      — Start Docker Compose services
    compose-down    — Stop Docker Compose services
    compose-status  — Show docker ps output
    e2e             — Run end-to-end scenario demo
    skills-test     — Run skill install tests (29/29)
    tests           — Run pytest test suite
    ppt             — Generate PPT presentation
    manifest        — Show task manifest (last e2e run)
    evidence        — List all evidence files
    screenshot      — Generate evidence screenshot report
"""

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DEPLOY_DIR = BASE_DIR / "poc" / "deploy"
EVIDENCE_DIR = BASE_DIR / "poc" / "evidence"
SCREENSHOTS_DIR = BASE_DIR / "poc" / "evidence" / "screenshots"
REQUIREMENTS = BASE_DIR / "requirements.txt"


def log(msg: str):
    print(msg)


def cmd_health() -> int:
    """Check health of all 8 services."""
    log("=" * 60)
    log("  DevPilot Loop — Service Health Check")
    log("=" * 60)
    urls = {
        "gateway":    ("http://localhost:8080/health", "Gateway"),
        "manager":    ("http://localhost:8008/health", "Manager (DevLead)"),
        "intake":     ("http://localhost:8001/health", "Intake"),
        "analyst":    ("http://localhost:8002/health", "Analyst"),
        "fixer":      ("http://localhost:8003/health", "Fixer"),
        "verifier":   ("http://localhost:8004/health", "Verifier"),
        "release":    ("http://localhost:8005/health", "Release"),
        "knowledge":  ("http://localhost:8006/health", "Knowledge"),
    }
    passed = 0
    failed = 0
    for name, (url, label) in urls.items():
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                status = data.get("status", "unknown")
                if status == "healthy":
                    log(f"  ✓ [{name:12s}] {label} — {status}")
                    passed += 1
                else:
                    log(f"  ? [{name:12s}] {label} — {status}")
                    failed += 1
        except Exception as e:
            log(f"  ✗ [{name:12s}] {label} — UNREACHABLE ({e})")
            failed += 1
    log("")
    log(f"  Result: {passed} healthy, {failed} unreachable / {len(urls)} total")
    return 0 if failed == 0 else 1


def cmd_compose_up() -> int:
    """Start all 8 Docker services."""
    log("Starting DevPilot Loop services...")
    r = subprocess.run(
        ["docker", "compose", "-f", str(DEPLOY_DIR / "docker-compose.yml"), "up", "-d"],
        cwd=str(BASE_DIR), capture_output=True, text=True
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    if r.returncode != 0:
        log("WARNING: docker compose up returned non-zero; checking if already running...")
        # Already running is fine
        pass
    # Wait for services to become healthy
    import time
    log("Waiting 15s for services to start...")
    time.sleep(15)
    return cmd_health()


def cmd_compose_down() -> int:
    """Stop all Docker services."""
    r = subprocess.run(
        ["docker", "compose", "-f", str(DEPLOY_DIR / "docker-compose.yml"), "down"],
        cwd=str(BASE_DIR), capture_output=True, text=True
    )
    print(r.stdout)
    return r.returncode


def cmd_compose_status() -> int:
    """Show running containers."""
    r = subprocess.run(
        ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
        capture_output=True, text=True
    )
    print(r.stdout)
    return 0


def cmd_e2e() -> int:
    """Run end-to-end scenario demo."""
    log("=" * 60)
    log("  DevPilot Loop — End-to-End Scenario Demo")
    log("=" * 60)
    r = subprocess.run(
        [str(BASE_DIR / ".venv" / "bin" / "python"),
         str(BASE_DIR / "poc" / "scenario" / "e2e_demo.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode


def cmd_skills_test() -> int:
    """Run skill install tests."""
    log("=" * 60)
    log("  DevPilot Loop — Skill Install Test")
    log("=" * 60)
    r = subprocess.run(
        [str(BASE_DIR / ".venv" / "bin" / "python"),
         str(BASE_DIR / "skills" / "install_test.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode


def cmd_tests() -> int:
    """Run pytest test suite."""
    log("=" * 60)
    log("  DevPilot Loop — Pytest Suite")
    log("=" * 60)
    r = subprocess.run(
        [str(BASE_DIR / ".venv" / "bin" / "python"), "-m", "pytest",
         str(BASE_DIR / "tests"), "-v", "--tb=short"],
        cwd=str(BASE_DIR), capture_output=True, text=True
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode


def cmd_ppt() -> int:
    """Generate PPT presentation."""
    log("=" * 60)
    log("  DevPilot Loop — PPT Generation")
    log("=" * 60)
    r = subprocess.run(
        [str(BASE_DIR / ".venv" / "bin" / "python"),
         str(BASE_DIR / "slides" / "generate_ppt.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode


def cmd_manifest() -> int:
    """Show last e2e task manifest."""
    m = BASE_DIR / "poc" / "scenario" / "task_manifest.json"
    if m.exists():
        with open(m) as f:
            data = json.load(f)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    else:
        log("No task_manifest.json found — run e2e demo first")
        return 1


def cmd_evidence() -> int:
    """List all evidence files."""
    log("Evidence files:")
    for p in sorted(EVIDENCE_DIR.rglob("*")):
        if p.is_file() and not p.name.startswith("."):
            rel = p.relative_to(BASE_DIR)
            size = p.stat().st_size
            log(f"  {rel}  ({size:,} bytes)")
    return 0


def cmd_screenshot() -> int:
    """Generate evidence screenshot report (text-based for headless)."""
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = SCREENSHOTS_DIR / f"screenshot_report_{now}.txt"
    with open(out, "w") as f:
        f.write(f"DevPilot Loop — Screenshot Report\n")
        f.write(f"Time: {datetime.now(timezone.utc).isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write("Services (curl /health):\n")
        urls = [
            ("gateway", "http://localhost:8080/health"),
            ("manager", "http://localhost:8008/health"),
            ("intake",  "http://localhost:8001/health"),
            ("analyst", "http://localhost:8002/health"),
            ("fixer",   "http://localhost:8003/health"),
            ("verifier","http://localhost:8004/health"),
            ("release", "http://localhost:8005/health"),
            ("knowledge","http://localhost:8006/health"),
        ]
        for name, url in urls:
            try:
                with urllib.request.urlopen(url, timeout=3) as resp:
                    data = json.loads(resp.read().decode())
                    f.write(f"  [{name}] status={data.get('status','?')} agent={data.get('agent','?')}\n")
            except Exception as e:
                f.write(f"  [{name}] ERROR: {e}\n")
        f.write("\nContainers:\n")
        r = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
                          capture_output=True, text=True)
        f.write(r.stdout)
    log(f"Screenshot report saved: {out}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    handlers = {
        "health":        cmd_health,
        "compose-up":    cmd_compose_up,
        "compose-down":  cmd_compose_down,
        "compose-status": cmd_compose_status,
        "e2e":           cmd_e2e,
        "skills-test":   cmd_skills_test,
        "tests":         cmd_tests,
        "ppt":           cmd_ppt,
        "manifest":      cmd_manifest,
        "evidence":      cmd_evidence,
        "screenshot":    cmd_screenshot,
    }
    fn = handlers.get(cmd)
    if fn is None:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)
    rc = fn()
    sys.exit(rc)


if __name__ == "__main__":
    main()
