"""
Deployment Guide
================
完整的部署文档
"""

import json
from datetime import datetime, timezone


DEPLOYMENT_ENVS = {
    "local": {
        "ports": {"manager": 8008, "intake": 8001, "analyst": 8002, "fixer": 8003, "verifier": 8004, "release": 8005, "knowledge": 8006},
        "compose_file": "docker-compose.yml",
        "cmd": "docker compose up -d",
    },
    "staging": {
        "ports": {"manager": 8008, "intake": 8001},
        "compose_file": "docker-compose.staging.yml",
        "cmd": "kubectl apply -f k8s/",
    },
    "production": {
        "ports": {"manager": 8008},
        "compose_file": None,
        "cmd": "kubectl apply -f k8s/prod/",
    },
}


SERVICE_PORT_MAPPINGS = {
    "devlead": 8008,
    "intake": 8001,
    "analyst": 8002,
    "fixer": 8003,
    "verifier": 8004,
    "release": 8005,
    "knowledge": 8006,
}


def generate_deployment_config(env: str = "local") -> dict:
    """生成部署配置"""
    config = DEPLOYMENT_ENVS.get(env, DEPLOYMENT_ENVS["local"])
    config["deployed_at"] = datetime.now(timezone.utc).isoformat()
    config["version"] = "2.0.0"
    return config


if __name__ == "__main__":
    for env in ["local", "staging", "production"]:
        print(f"\n=== {env.upper()} ===")
        print(json.dumps(generate_deployment_config(env), indent=2))
