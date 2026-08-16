# DevPilot Loop API Reference
============================

## Base URLs
- Manager: `http://localhost:8008`
- Intake: `http://localhost:8001`
- Analyst: `http://localhost:8002`
- Fixer: `http://localhost:8003`
- Verifier: `http://localhost:8004`
- Release: `http://localhost:8005`
- Knowledge: `http://localhost:8006`

## Manager Endpoints

### GET /health
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "agent": "devlead",
  "type": "manager",
  "uptime_seconds": 3600,
  "version": "2.0.0",
  "dal_level": "DAL-2",
  "metrics": {
    "tasks_received": 42,
    "tasks_dispatched": 42,
    "results_submitted": 38,
    "errors": 0
  }
}
```

### GET /metrics
Returns Prometheus-compatible metrics.

**Response:**
```json
{
  "tasks_received": 42,
  "tasks_dispatched": 42,
  "results_submitted": 38,
  "errors": 0,
  "uptime_seconds": 3600,
  "memory_usage_mb": 120.5
}
```

### POST /dispatch
Dispatch a task to a worker.

**Request:**
```json
{
  "task_id": "TASK-001",
  "source": "issue|ci|alert|manual",
  "raw_payload": {"issue": "...", "repo": "..."},
  "priority": "P1|P2|P3",
  "target_worker": "intake|analyst|fixer|verifier|release|knowledge",
  "trace_id": "trace-abc123",
  "approval_required": false,
  "metadata": {}
}
```

**Response:**
```json
{
  "status": "ok",
  "task_id": "TASK-001",
  "target": "intake",
  "trace_id": "trace-abc123"
}
```

### GET /tasks
List all tasks with optional status filter.

**Query Params:**
- `status`: Filter by status (dispatched, received, completed, etc.)

**Response:**
```json
{
  "tasks": [...],
  "count": 42
}
```

### GET /logs
Retrieve execution logs.

**Query Params:**
- `limit`: Number of logs (default: 50)
- `level`: Log level filter (DEBUG, INFO, WARNING, ERROR, AUDIT)

**Response:**
```json
{
  "logs": [...],
  "total": 100,
  "filtered": 50
}
```

### GET /approval
Get pending approval requests.

**Response:**
```json
{
  "pending": [...],
  "count": 2
}
```

### POST /approve/{task_id}
Approve a pending task.

**Form Data:**
- `notes`: Approval notes

**Response:**
```json
{
  "status": "ok",
  "task_id": "TASK-001"
}
```

### POST /reject/{task_id}
Reject a pending task.

**Form Data:**
- `notes`: Rejection notes

**Response:**
```json
{
  "status": "ok",
  "task_id": "TASK-001"
}
```

### POST /register_worker
Register a new worker agent.

**Form Data:**
- `name`: Worker name
- `worker_type`: Worker type

**Response:**
```json
{
  "status": "ok",
  "agent": "worker-name",
  "type": "worker"
}
```

## Worker Endpoints

### POST /task
Receive a task from manager.

**Request:**
```json
{
  "task_id": "TASK-001",
  "source": "issue",
  "raw_payload": {...},
  "priority": "P1",
  "trace_id": "trace-abc123"
}
```

**Response:**
```json
{
  "status": "ok",
  "task_id": "TASK-001",
  "trace_id": "trace-abc123"
}
```

### POST /result
Submit execution result.

**Request:**
```json
{
  "task_id": "TASK-001",
  "agent_name": "intake",
  "output": {...},
  "status": "ok|failed|cancelled|pending_approval",
  "trace_id": "trace-abc123",
  "confidence": 0.95,
  "evidence": [],
  "approval_notes": ""
}
```

**Response:**
```json
{
  "status": "ok",
  "result_id": "uuid",
  "trace_id": "trace-abc123"
}
```

### GET /agents
List current agent tasks.

**Response:**
```json
{
  "agents": [...],
  "count": 5,
  "agent": "intake"
}
```

### GET /skills
List installed skills.

**Response:**
```json
{
  "skills": [
    {"name": "triage", "version": "1.0.0", "agent": "intake"}
  ],
  "count": 1
}
```

## Data Models

### TaskRequest
```typescript
interface TaskRequest {
  task_id: string;
  source: "issue" | "ci" | "alert" | "manual";
  raw_payload: Record<string, any>;
  priority: "P1" | "P2" | "P3";
  trace_id?: string;
  target_worker?: string;
  approval_required?: boolean;
  metadata?: Record<string, any>;
}
```

### ResultResponse
```typescript
interface ResultResponse {
  task_id: string;
  agent_name: string;
  output: Record<string, any>;
  status: "ok" | "failed" | "cancelled" | "pending_approval";
  trace_id?: string;
  confidence?: number;
  evidence?: string[];
  approval_notes?: string;
}
```

## Error Responses
| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error |
