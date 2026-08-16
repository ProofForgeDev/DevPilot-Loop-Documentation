# 证据收集程序

## L1 证据收集

### 截图
```bash
# 健康检查截图
python3 scripts/capture_screenshot.py --target health_dashboard --output evidence/l1/screenshots/health_dashboard.png

# Docker Compose 状态
docker compose ps --format json | jq . > evidence/l1/docker_compose_state.json

# Matrix 房间消息
matrix-client get-messages --room #devpilot --limit 100 > evidence/l1/matrix_messages.json
```

### 日志
```bash
# 服务启动日志
docker compose logs --tail 100 > evidence/l1/service_startup.log

# 任务派发日志
tail -f /var/log/devpilot/dispatch.log > evidence/l1/task_dispatch.log

# 安全事件日志
docker logs higress | grep -i security > evidence/l1/security_events.log
```

## L2 证据收集

### Agent 配置
```bash
# 导出所有 Agent 配置
for agent in devlead intake analyst fixer verifier release knowledge orchestrator lifecycle; do
    cat agents/$agent/config.yaml >> evidence/l2/agent_configs.txt
done
```

### 通信测试
```bash
# 执行 5 项通信测试
python3 tests/test_communication.py --output evidence/l2/comm_test_results.txt
```

### API 规范
```bash
# 生成 OpenAPI 规范
python3 scripts/generate_openapi.py > evidence/l2/api_spec.json
```

## L3 证据收集

### 架构分析
```bash
# 生成调用图
python3 scripts/analyze_calls.py --output evidence/l3/call_graph.md

# 威胁建模
python3 scripts/threat_model.py --framework STRIDE --output evidence/l3/threat_model.md
```

### DAL 模型验证
```bash
# 验证 DAL-2 属性
python3 scripts/verify_dal2.py > evidence/l3/dal2_verification.md
```

## L4 证据收集

### 安全审计
```bash
# Bandit 扫描
bandit -r skills/ poc/ --json > evidence/l4/bandit_results.json

# Safety 检查
safety check --json > evidence/l4/safety_results.json

# Trivy 扫描
trivy image devpilot-devlead:latest --format json > evidence/l4/trivy_results.json

# Semgrep 规则
semgrep --config=p/community --json > evidence/l4/semgrep_results.json
```

### 性能基准
```bash
# Locust 负载测试
locust -f tests/locustfiles/perf_test.py --headless --users 10 --spawn-rate 2 --run-time 60s --csv evidence/l4/locust_results

# pytest-benchmark
pytest --benchmark-json evidence/l4/benchmark_results.json
```

### 代码质量
```bash
# Radon 复杂度
radon cc skills/ --json > evidence/l4/radon_results.json

# Pylint
pylint skills/ --output-format=json > evidence/l4/pylint_results.json

# McCabe 圈复杂度
python3 -m mccabe skills/ --min 10 > evidence/l4/mccabe_results.txt
```

## 证据验证流程

1. **收集**: 按上述程序生成原始证据
2. **校验**: 运行 checksum 验证完整性
   ```bash
   sha256sum evidence/l4/*.json > evidence/.checksums
   ```
3. **索引**: 更新 `evidence_index.json`
4. **归档**: 备份至 `archive/YYYY-MM-DD/`
