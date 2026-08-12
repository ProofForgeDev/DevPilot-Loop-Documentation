"""部署验证 Skill — deploy-verification
========================================
验证部署健康状态，检查回滚策略，确保部署可靠。
"""

from skills.base import BaseSkill
import urllib.request
import json


class DeployVerificationSkill(BaseSkill):
    name = "deploy-verification"
    version = "1.0.0"
    description = "部署验证：健康检查、回滚策略、服务状态验证"

    def execute(self, input_data: dict) -> dict:
        base_url = input_data.get("base_url", "")
        services = input_data.get("services", [])
        check_health = input_data.get("check_health", True)

        results = []
        if check_health and base_url:
            for svc in services:
                url = f"{base_url.rstrip('/')}/health"
                try:
                    with urllib.request.urlopen(url, timeout=5) as resp:
                        data = json.loads(resp.read().decode())
                        results.append({
                            "service": svc,
                            "url": url,
                            "status": "healthy" if data.get("status") == "healthy" else "unhealthy",
                            "response_time_ms": round(resp.headers.get("Content-Length", 0), 2),
                        })
                except Exception as e:
                    results.append({
                        "service": svc,
                        "url": url,
                        "status": "error",
                        "error": str(e),
                    })

        rollback_plan = {
            "strategy": input_data.get("rollback_strategy", "blue_green"),
            "steps": [
                "Stop new deployment",
                "Restore previous image tag",
                "Verify health checks",
                "Monitor error rates for 5 minutes",
            ],
        }

        all_healthy = all(r["status"] == "healthy" for r in results) if results else False

        return {
            "skill": self.name,
            "version": self.version,
            "check_performed": check_health,
            "services_checked": len(results),
            "results": results,
            "rollback_plan": rollback_plan,
            "overall_status": "PASS" if all_healthy else ("NEEDS_CHECK" if not results else "FAIL"),
            "status": "ok",
        }

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and ("base_url" in input_data or "services" in input_data)

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "properties": {
                    "base_url": {"type": "string", "description": "服务基础 URL"},
                    "services": {"type": "array", "items": {"type": "string"}, "description": "要检查的服务列表"},
                    "check_health": {"type": "boolean", "default": True},
                    "rollback_strategy": {"type": "string", "enum": ["blue_green", "canary", "rolling"], "default": "blue_green"},
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "services_checked": {"type": "integer"},
                    "overall_status": {"type": "string", "enum": ["PASS", "FAIL", "NEEDS_CHECK"]},
                    "rollback_plan": {"type": "object"},
                    "status": {"type": "string"},
                },
            },
        }
