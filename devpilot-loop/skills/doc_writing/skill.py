"""文档编写 Skill — doc-writing (Deep)
=======================================
生成 API 文档、变更日志、README 等文档内容。
支持多种文档类型、模板、自动格式化。
"""

from skills.base import BaseSkill
from datetime import datetime, timezone
import logging
from typing import Any

logger = logging.getLogger("devpilot.skills")


class DocWritingSkill(BaseSkill):
    name = "doc-writing"
    version = "2.0.0"
    description = "文档编写：API/Changelog/README/SPEC 自动生成、模板化、格式化"

    # 文档模板
    TEMPLATES = {
        "api": {
            "title": "API Documentation",
            "sections": ["Overview", "Endpoints", "Request", "Response", "Examples", "Errors"],
            "format": "markdown",
        },
        "changelog": {
            "title": "Changelog",
            "sections": ["Version", "Features", "Fixes", "Breaking", "Migration"],
            "format": "markdown",
        },
        "readme": {
            "title": "README",
            "sections": ["Description", "Installation", "Usage", "API", "Contributing", "License"],
            "format": "markdown",
        },
        "spec": {
            "title": "Technical Specification",
            "sections": ["Overview", "Architecture", "Components", "API", "Security", "Deployment"],
            "format": "markdown",
        },
        "runbook": {
            "title": "Runbook",
            "sections": ["Overview", "Prerequisites", "Steps", "Troubleshooting", "Rollback"],
            "format": "markdown",
        },
    }

    def execute(self, input_data: dict) -> dict:
        try:
            if not self.validate_input(input_data):
                logger.error("doc-writing: invalid input")
                return {"status": "error", "error": "invalid_input", "skill": self.name, "version": self.version}

            doc_type = input_data.get("doc_type", "api")
            content = input_data.get("content", "")
            title = input_data.get("title", "Untitled")
            options = input_data.get("options", {})

            template = self.TEMPLATES.get(doc_type, self.TEMPLATES["api"])
            format_style = options.get("format", template["format"])
            include_examples = options.get("include_examples", True)
            include_api_spec = options.get("include_api_spec", True)

            # 生成文档
            if doc_type == "changelog":
                document = self._generate_changelog(title, content, options)
            elif doc_type == "api":
                document = self._generate_api_doc(title, content, options)
            elif doc_type == "readme":
                document = self._generate_readme(title, content, options)
            elif doc_type == "spec":
                document = self._generate_spec(title, content, options)
            elif doc_type == "runbook":
                document = self._generate_runbook(title, content, options)
            else:
                document = self._generate_generic(title, content, options)

            # 生成元数据
            metadata = self._generate_metadata(doc_type, title, options)

            return {
                "skill": self.name,
                "version": self.version,
                "doc_type": doc_type,
                "title": title,
                "document": document,
                "doc_length": len(document),
                "word_count": len(document.split()),
                "metadata": metadata,
                "template_used": template["title"],
                "sections": template["sections"],
                "status": "ok",
            }
        except Exception as e:
            logger.error(f"doc-writing: execution failed: {e}")
            return {"status": "error", "error": str(e), "skill": self.name, "version": self.version}

    def _generate_changelog(self, title: str, content: str, options: dict) -> str:
        """生成变更日志"""
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        version = options.get("version", "1.0.0")

        changelog = f"""# Changelog — {title}

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [{version}] — {date}

### Added
- Initial project structure
- Core functionality

### Changed
{content if content else "- Updated based on provided content"}

### Deprecated
- (None)

### Removed
- (None)

### Fixed
- Bug fixes and improvements

### Security
- Security improvements

---

## [Previous Versions]

### Maintenance releases
- Various bug fixes and improvements
"""
        return changelog

    def _generate_api_doc(self, title: str, content: str, options: dict) -> str:
        """生成 API 文档"""
        api_doc = f"""# API Documentation — {title}

## Overview
{content[:500] if content else "API documentation for the service."}

## Authentication
All API requests require authentication via Bearer token.

```bash
Authorization: Bearer <your-token>
```

## Endpoints

### Base URL
```
{options.get('base_url', 'http://localhost:8008')}
```

### Health Check
- **Method:** GET
- **Path:** `/health`
- **Description:** Check service health status
- **Response:** 200 OK

```json
{{
  "status": "healthy",
  "agent": "{options.get('agent', 'devlead')}",
  "version": "2.0.0"
}}
```

### Task Dispatch
- **Method:** POST
- **Path:** `/dispatch`
- **Description:** Dispatch a task to a worker
- **Request Body:**
```json
{{
  "task_id": "string",
  "source": "issue|ci|alert|manual",
  "raw_payload": {{}},
  "priority": "P1|P2|P3",
  "target_worker": "string",
  "trace_id": "string"
}}
```
- **Response:** 200 OK

```json
{{
  "status": "ok",
  "task_id": "string",
  "target": "string",
  "trace_id": "string"
}}
```

## Error Responses
| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

## Rate Limiting
- **Limit:** 100 requests per minute
- **Header:** `X-RateLimit-Limit`

---
*Generated by {self.name} v{self.version} at {datetime.now(timezone.utc).isoformat()}*
"""
        return api_doc

    def _generate_readme(self, title: str, content: str, options: dict) -> str:
        """生成 README"""
        readme = f"""# {title}

> {content[:200] if content else "A multi-agent autonomous system for software R&D."}

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features
- ✅ Multi-agent orchestration (Manager + 6 Workers)
- ✅ HiClaw API compatible runtime
- ✅ 6 installable skills (Code Review, Security Scan, etc.)
- ✅ Complete observability (OTel tracing, metrics, logging)
- ✅ Zero-trust security (RBAC, credential management)
- ✅ Docker-based deployment
- ✅ Competition-ready evidence package

## Architecture
```
┌─────────────┐     ┌─────────────┐
│   Manager   │────▶│   Worker    │
│  (devlead)  │     │   (intake)  │
└─────────────┘     └─────────────┘
       │
┌──────┴──────┐     ┌─────────────┐     ┌─────────────┐
│   Analyst   │────▶│    Fixer    │────▶│  Verifier   │
└─────────────┘     └─────────────┘     └─────────────┘
                                                  │
                                          ┌───────┴───────┐
                                          │   Release     │
                                          └───────────────┘
```

## Installation
```bash
# Clone repository
git clone https://github.com/ProofForgeDev/DevPilot-Loop-Documentation.git
cd devpilot-loop

# Install dependencies
pip install -e "skills[dev]"

# Start services
docker compose up -d
```

## Usage
```bash
# Check service health
curl http://localhost:8008/health

# Dispatch a task
curl -X POST http://localhost:8008/dispatch \
  -H 'Content-Type: application/json' \
  -d '{...}'
```

## Testing
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run skill tests
python3 tests/test_skills_validation.py
```

## API Reference
See [docs/04-skills.md](docs/04-skills.md) for detailed API documentation.

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Version 2.0.0 | Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d")}*
"""
        return readme

    def _generate_spec(self, title: str, content: str, options: dict) -> str:
        """生成技术规格文档"""
        spec = f"""# Technical Specification — {title}

## 1. Overview
{content[:500] if content else "Technical specification for the system."}

## 2. Architecture
### 2.1 System Components
- **Manager**: Central orchestration and task distribution
- **Workers**: Specialized agents for different tasks
- **Gateway**: External interface and authentication

### 2.2 Communication Pattern
- Synchronous: HTTP/REST for task dispatch
- Asynchronous: Queue-based for long-running tasks
- Observability: OpenTelemetry tracing

## 3. API Design
### 3.1 RESTful Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /dispatch | Task dispatch |
| POST | /result | Result submission |
| GET | /tasks | Task listing |
| GET | /logs | Log retrieval |

### 3.2 Data Models
See [schemas/](schemas/) for detailed model definitions.

## 4. Security
### 4.1 Authentication
- JWT Bearer tokens
- mTLS for inter-service communication
- RBAC (L1/L2/L3)

### 4.2 Data Protection
- Credential hashing (SHA-256)
- Encrypted storage
- Audit logging

## 5. Deployment
### 5.1 Docker Compose
See [docker-compose.yml](docker-compose.yml) for full configuration.

### 5.2 Kubernetes
See [k8s/](k8s/) for production manifests.

## 6. Monitoring
- Prometheus metrics
- OpenTelemetry tracing
- Structured JSON logging

---
*Specification v{options.get("version", "1.0.0")} | {datetime.now(timezone.utc).strftime("%Y-%m-%d")}*
"""
        return spec

    def _generate_runbook(self, title: str, content: str, options: dict) -> str:
        """生成运维手册"""
        runbook = f"""# Runbook — {title}

## Overview
{content[:300] if content else "Operational runbook for the system."}

## Prerequisites
- Docker and Docker Compose installed
- Access to all service endpoints
- Monitoring dashboard access

## Standard Operating Procedures

### 1. Service Health Check
```bash
curl http://localhost:8008/health
curl http://localhost:8001/health
# ... repeat for all services
```

### 2. Task Dispatch
```bash
curl -X POST http://localhost:8008/dispatch \
  -H 'Content-Type: application/json' \
  -d '{{"task_id":"T-001","source":"manual","raw_payload":{{"issue":"test"}},"priority":"P1","target_worker":"intake"}}'
```

### 3. Monitor Logs
```bash
curl http://localhost:8008/logs?limit=50
```

## Troubleshooting

### Service Unreachable
1. Check Docker containers: `docker compose ps`
2. Restart failed services: `docker compose restart <service>`
3. View logs: `docker compose logs <service>`

### High Error Rate
1. Check metrics: `curl http://localhost:8008/metrics`
2. Review error logs: `curl http://localhost:8008/logs?level=ERROR`
3. Analyze traces: Check trace dashboard

## Rollback Procedure
1. Stop current deployment
2. Restore previous version
3. Verify health checks
4. Monitor for 5 minutes

## Emergency Contacts
- On-call: see PagerDuty
- Slack: #devpilot-incidents

---
*Runbook v1.0 | Last updated {datetime.now(timezone.utc).strftime("%Y-%m-%d")}*
"""
        return runbook

    def _generate_generic(self, title: str, content: str, options: dict) -> str:
        """生成通用文档"""
        return f"""# {title}

{content}

---
*Generated by {self.name} v{self.version} at {datetime.now(timezone.utc).isoformat()}*
"""

    def _generate_metadata(self, doc_type: str, title: str, options: dict) -> dict:
        """生成文档元数据"""
        return {
            "type": doc_type,
            "title": title,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": options.get("version", "1.0.0"),
            "format": options.get("format", "markdown"),
            "author": options.get("author", "DevPilot Loop"),
            "keywords": [doc_type, "documentation", "api", "reference"],
        }

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and "doc_type" in input_data and "title" in input_data

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "required": ["doc_type", "title"],
                "properties": {
                    "doc_type": {"type": "string", "enum": ["api", "changelog", "readme", "spec", "runbook"]},
                    "title": {"type": "string", "description": "文档标题"},
                    "content": {"type": "string", "description": "源内容（可选）"},
                    "options": {
                        "type": "object",
                        "properties": {
                            "version": {"type": "string", "description": "文档版本"},
                            "format": {"type": "string", "description": "输出格式"},
                            "include_examples": {"type": "boolean"},
                            "include_api_spec": {"type": "boolean"},
                        }
                    }
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "version": {"type": "string"},
                    "doc_type": {"type": "string"},
                    "title": {"type": "string"},
                    "document": {"type": "string"},
                    "doc_length": {"type": "integer"},
                    "word_count": {"type": "integer"},
                    "metadata": {"type": "object"},
                    "template_used": {"type": "string"},
                    "sections": {"type": "array"},
                    "status": {"type": "string"},
                },
            },
        }
