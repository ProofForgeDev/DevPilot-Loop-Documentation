"""部署验证 Skill — deploy-verification (Deep)
================================================
验证部署健康状态，检查回滚策略，确保部署可靠。
支持蓝绿部署、金丝雀发布、滚动更新等多种策略。
"""

from skills.base import BaseSkill
import urllib.request
import json
from datetime import datetime, timezone
from typing import Any


class DeployVerificationSkill(BaseSkill):
    name = "deploy-verification"
    version = "2.0.0"
    description = "部署验证：健康检查、回滚策略、金丝雀发布、蓝绿部署"

    # 部署策略
    DEPLOYMENT_STRATEGIES = {
        "blue_green": {
            "name": "Blue-Green Deployment",
            "description": "同时运行两个环境，通过切换流量实现零停机部署",
            "steps": [
                "Deploy to green environment",
                "Run health checks on green",
                "Switch traffic from blue to green",
                "Monitor for errors",
                "Keep blue as rollback option",
            ],
        },
        "canary": {
            "name": "Canary Deployment",
            "description": "逐步放量，先向小部分用户发布，确认无误后再全量",
            "steps": [
                "Deploy to canary instances (10%)",
                "Monitor error rates and metrics",
                "Gradually increase traffic (25%, 50%, 75%)",
                "Full rollout if all checks pass",
                "Automatic rollback on failure",
            ],
        },
        "rolling": {
            "name": "Rolling Update",
            "description": "逐个替换旧实例，保持服务可用",
            "steps": [
                "Stop one old instance",
                "Start new instance",
                "Verify health check",
                "Repeat for all instances",
                "Clean up old instances",
            ],
        },
    }

    # 健康检查端点
    HEALTH_ENDPOINTS = {
        "manager": "/health",
        "intake": "/health",
        "analyst": "/health",
        "fixer": "/health",
        "verifier": "/health",
        "release": "/health",
        "knowledge": "/health",
    }

    def execute(self, input_data: dict) -> dict:
        base_url = input_data.get("base_url", "")
        services = input_data.get("services", [])
        options = input_data.get("options", {})

        check_health = options.get("check_health", True)
        check_dependencies = options.get("check_dependencies", True)
        strategy = options.get("strategy", "blue_green")
        canary_percentage = options.get("canary_percentage", 10)

        results = []
        dependencies = []
        warnings = []

        # 健康检查
        if check_health and base_url:
            results = self._check_health(base_url, services)
            warnings.extend(self._analyze_results(results))

        # 依赖检查
        if check_dependencies:
            dependencies = self._check_dependencies(base_url, services)

        # 部署策略验证
        strategy_config = self.DEPLOYMENT_STRATEGIES.get(strategy, self.DEPLOYMENT_STRATEGIES["blue_green"])

        # 回滚计划
        rollback_plan = self._generate_rollback_plan(strategy, services, results)

        # 综合评估
        overall_status = self._evaluate_overall(results, dependencies, warnings)
        risk_level = self._calculate_risk(results, dependencies)

        return {
            "skill": self.name,
            "version": self.version,
            "strategy": strategy_config["name"],
            "strategy_description": strategy_config["description"],
            "check_performed": check_health,
            "services_checked": len(results),
            "results": results,
            "dependencies": dependencies,
            "warnings": warnings,
            "rollback_plan": rollback_plan,
            "deployment_steps": strategy_config["steps"],
            "overall_status": overall_status,
            "risk_level": risk_level,
            "canary_percentage": canary_percentage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "ok",
        }

    def _check_health(self, base_url: str, services: list) -> list:
        """执行健康检查"""
        results = []

        for svc in services:
            url = f"{base_url.rstrip('/')}/{self.HEALTH_ENDPOINTS.get(svc, 'health')}"
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    results.append({
                        "service": svc,
                        "url": url,
                        "status": data.get("status", "unknown"),
                        "agent": data.get("agent", "unknown"),
                        "type": data.get("type", "unknown"),
                        "version": data.get("version", "unknown"),
                        "uptime_seconds": data.get("uptime_seconds", 0),
                        "checked_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as e:
                results.append({
                    "service": svc,
                    "url": url,
                    "status": "error",
                    "error": str(e),
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                })

        return results

    def _check_dependencies(self, base_url: str, services: list) -> list:
        """检查服务依赖"""
        deps = []
        # 简化版：检查所有服务是否可互相访问
        for svc in services:
            deps.append({
                "service": svc,
                "dependency": "database",
                "status": "unknown",
                "note": "Dependency check requires database access",
            })
            deps.append({
                "service": svc,
                "dependency": "message_queue",
                "status": "unknown",
                "note": "Message queue dependency not configured",
            })
        return deps

    def _analyze_results(self, results: list) -> list:
        """分析检查结果并生成警告"""
        warnings = []
        for r in results:
            if r["status"] == "error":
                warnings.append(f"Service {r['service']} health check failed: {r.get('error', 'Unknown')}")
            elif r["status"] == "unhealthy":
                warnings.append(f"Service {r['service']} is unhealthy")
            elif r.get("uptime_seconds", 0) < 60:
                warnings.append(f"Service {r['service']} uptime is low ({r['uptime_seconds']}s)")
        return warnings

    def _generate_rollback_plan(self, strategy: str, services: list, results: list) -> dict:
        """生成回滚计划"""
        healthy_services = [r["service"] for r in results if r["status"] == "healthy"]
        unhealthy_services = [r["service"] for r in results if r["status"] != "healthy"]

        rollback = {
            "strategy": strategy,
            "trigger_conditions": [
                "Error rate > 5%",
                "P99 latency > 1000ms",
                "Health check failures > 2 consecutive",
                "Business metric degradation",
            ],
            "steps": [
                "Identify last known good version",
                f"Stop deploying to: {', '.join(unhealthy_services) if unhealthy_services else 'all'}",
                "Restore previous image/tag",
                "Verify health checks pass",
                "Monitor error rates for 5 minutes",
                "Notify stakeholders",
            ],
            "estimated_rollback_time_minutes": 5,
            "healthy_services_count": len(healthy_services),
            "unhealthy_services_count": len(unhealthy_services),
        }
        return rollback

    def _evaluate_overall(self, results: list, dependencies: list, warnings: list) -> str:
        """综合评估"""
        if not results:
            return "NEEDS_CHECK"

        healthy_count = sum(1 for r in results if r["status"] == "healthy")
        error_count = sum(1 for r in results if r["status"] == "error")
        total = len(results)

        if error_count == 0 and healthy_count == total:
            return "PASS"
        elif error_count > total * 0.5:
            return "FAIL"
        elif warnings:
            return "WARNING"
        else:
            return "PASS_WITH_WARNINGS"

    def _calculate_risk(self, results: list, dependencies: list) -> str:
        """计算风险等级"""
        if not results:
            return "UNKNOWN"

        error_ratio = sum(1 for r in results if r["status"] != "healthy") / len(results)

        if error_ratio > 0.5:
            return "CRITICAL"
        elif error_ratio > 0.2:
            return "HIGH"
        elif error_ratio > 0.1:
            return "MEDIUM"
        else:
            return "LOW"

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and ("base_url" in input_data or "services" in input_data)

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "properties": {
                    "base_url": {"type": "string", "description": "服务基础 URL"},
                    "services": {"type": "array", "items": {"type": "string"}, "description": "要检查的服务列表"},
                    "options": {
                        "type": "object",
                        "properties": {
                            "check_health": {"type": "boolean", "description": "执行健康检查"},
                            "check_dependencies": {"type": "boolean", "description": "检查依赖"},
                            "strategy": {"type": "string", "enum": ["blue_green", "canary", "rolling"]},
                            "canary_percentage": {"type": "integer", "description": "金丝雀流量百分比"},
                        }
                    }
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "version": {"type": "string"},
                    "strategy": {"type": "string"},
                    "check_performed": {"type": "boolean"},
                    "services_checked": {"type": "integer"},
                    "results": {"type": "array"},
                    "dependencies": {"type": "array"},
                    "warnings": {"type": "array"},
                    "rollback_plan": {"type": "object"},
                    "deployment_steps": {"type": "array"},
                    "overall_status": {"type": "string", "enum": ["PASS", "FAIL", "WARNING", "NEEDS_CHECK"]},
                    "risk_level": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"]},
                    "timestamp": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
        }
