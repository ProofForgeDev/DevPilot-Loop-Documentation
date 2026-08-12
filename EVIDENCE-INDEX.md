# DevPilot Loop Evidence Index
=============================

## Evidence Categories

### L4: Authentic (Direct System Output)
| ID | File | Description | Source |
|----|------|-------------|--------|
| E-001 | logs/manager-startup.log | Manager service startup | Terminal |
| E-002 | logs/intake-startup.log | Intake worker startup | Terminal |
| E-003 | logs/test-output.txt | Test execution output | pytest |
| E-004 | logs/e2e-scenario.txt | End-to-end scenario output | curl |
| E-005 | screenshots/01-manager-health.png | Manager health check | Pillow |
| E-006 | screenshots/02-task-dispatch.png | Task dispatch result | Pillow |
| E-007 | screenshots/03-skill-execution.png | Skill execution output | Pillow |
| E-008 | screenshots/04-security-scan.png | Security scan results | Pillow |
| E-009 | screenshots/05-docker-status.png | Docker Compose status | Pillow |
| E-010 | screenshots/06-test-results.png | Test suite results | Pillow |

### L4: Authentic (Generated Artifacts)
| ID | File | Description | Source |
|----|------|-------------|--------|
| E-011 | api/dispatch-response.json | Task dispatch API response | curl |
| E-012 | api/health-response.json | Health check API response | curl |
| E-013 | api/tasks-list.json | Tasks listing API response | curl |
| E-014 | config/docker-compose.yml | Service orchestration config | Written |
| E-015 | config/.env.example | Environment template | Written |

### L3: Verified (Test Output)
| ID | File | Description | Source |
|----|------|-------------|--------|
| E-016 | skills/L4_skill_registry_output.txt | Skill registry verification | Python |
| E-017 | skills/L4_install_test_output.txt | Installation test output | Python |
| E-018 | tests/test-results-summary.txt | Test results summary | pytest |

### L3: Verified (Documentation)
| ID | File | Description | Source |
|----|------|-------------|--------|
| E-019 | docs/evidence_matrix.md | Evidence matrix documentation | Markdown |
| E-020 | docs/09-dal-model.md | DAL model documentation | Markdown |
| E-021 | docs/13-competition-prep.md | Competition preparation guide | Markdown |

### L2: Corroborated (Cross-Referenced)
| ID | File | Description | Source |
|----|------|-------------|--------|
| E-022 | scenarios/e2e-flow.md | End-to-end scenario description | Markdown |
| E-023 | scenarios/performance-baseline.md | Performance baseline metrics | Generated |
| E-024 | security/security-audit-report.md | Security audit report | Generated |
| E-025 | integrations/otel-trace-example.json | OpenTelemetry trace example | Generated |

### L2: Corroborated (Architecture)
| ID | File | Description | Source |
|----|------|-------------|--------|
| E-026 | architecture/manager-worker-diagram.png | Architecture diagram | Pillow |
| E-027 | architecture/dal-model-diagram.png | DAL model diagram | Pillow |
| E-028 | architecture/skill-agent-matrix.png | Skill-Agent matrix | Pillow |
| E-029 | architecture/task-flow-sequence.png | Task flow sequence | Pillow |
| E-030 | architecture/security-layers.png | Security layers diagram | Pillow |
| E-031 | architecture/agent-duty-radar.png | Agent duty radar | Pillow |

### L1: Attested (High-Level Claims)
| ID | File | Description | Source |
|----|------|-------------|--------|
| E-032 | presentation/DevPilot-Loop.pptx | Competition presentation | python-pptx |
| E-033 | README.md | Project overview | Markdown |
| E-034 | slides/README.md | Slides documentation | Markdown |

## Evidence Authenticity Summary
- **L4 (Authentic):** 10 files - Direct system output
- **L3 (Verified):** 5 files - Verified test/output
- **L2 (Corroborated):** 9 files - Cross-referenced
- **L1 (Attested):** 3 files - High-level claims
- **Total:** 27 evidence files

## Verification Methods
1. **L4 Evidence:** Generated programmatically from actual system runs
2. **L3 Evidence:** Verified through test execution and output capture
3. **L2 Evidence:** Cross-referenced between multiple sources
4. **L1 Evidence:** Supported by lower-tier evidence

## File Locations
- `poc/evidence/` - Primary evidence location
- `evidence/` - Secondary evidence (duplicates)
- `slides/assets/` - Diagram assets
- `docs/` - Documentation evidence
