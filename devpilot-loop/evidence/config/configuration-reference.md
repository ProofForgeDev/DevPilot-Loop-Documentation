# DevPilot Loop Configuration Reference
=========================================

## Environment Variables

### Manager (devlead)
| Variable | Value | Description |
|----------|-------|-------------|
| AGENT_NAME | devlead | Agent identifier |
| AGENT_TYPE | manager | Agent type |
| PORT | 8008 | Service port |
| PERMISSION_LEVEL | L3 | Permission level |
| TRACE_ID | auto | Trace ID (auto-generated) |
| LOG_LEVEL | INFO | Logging level |
| MAX_WORKERS | 10 | Max concurrent workers |

### Workers
| Variable | Value | Description |
|----------|-------|-------------|
| AGENT_NAME | intake/analyst/fixer/verifier/release/knowledge | Agent identifier |
| AGENT_TYPE | worker | Agent type |
| SKILL_NAME | triage/root-cause/patch/test/deploy/doc | Associated skill |
| PORT | 8001-8006 | Service port |
| PERMISSION_LEVEL | L1/L2 | Permission level |
| TRACE_ID | auto | Trace ID (auto-generated) |
| LOG_LEVEL | INFO | Logging level |

### Security
| Variable | Value | Description |
|----------|-------|-------------|
| JWT_SECRET | *required* | JWT signing secret |
| CREDENTIAL_STORE_PATH | /tmp/devpilot-credentials.json | Credential storage |
| ENABLE_MTLS | false | Enable mTLS (production) |
| ALLOWED_ORIGINS | * | CORS allowed origins |

### Observability
| Variable | Value | Description |
|----------|-------|-------------|
| OTEL_ENABLED | true | Enable OpenTelemetry |
| OTEL_EXPORTER | console | Exporter type |
| OTEL_SERVICE_NAME | devpilot-loop | Service name for traces |
| METRICS_ENABLED | true | Enable metrics export |

## Docker Compose Configuration

### Services
```yaml
services:
  devlead:
    image: devpilot-loop/devlead:latest
    ports:
      - "8008:8008"
    environment:
      - AGENT_NAME=devlead
      - AGENT_TYPE=manager
      - PORT=8008
      - PERMISSION_LEVEL=L3

  intake:
    image: devpilot-loop/worker:latest
    ports:
      - "8001:8001"
    environment:
      - AGENT_NAME=intake
      - AGENT_TYPE=worker
      - SKILL_NAME=triage
      - PORT=8001
      - PERMISSION_LEVEL=L1
```

### Networks
- `devpilot-network`: Internal service communication
- `devpilot-external`: External API exposure

### Volumes
- `credentials`: Credential storage
- `logs`: Log persistence
- `data`: Application data

## Kubernetes Configuration

### Deployment
- Replica count: 1 (manager), 1 (each worker)
- Resource limits: 500m CPU, 512MB memory
- Health checks: HTTP /health endpoint
- Pod disruption budget: 1 max unavailable

### Services
- ClusterIP for internal communication
- LoadBalancer for external access (optional)

### ConfigMap
- Environment variables
- Feature flags
- Logging configuration

### Secret
- JWT tokens
- API keys
- TLS certificates
