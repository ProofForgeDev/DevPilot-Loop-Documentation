# 审计工具版本

## 安全扫描工具

| 工具 | 版本 | 用途 | 规则数 |
|------|------|------|--------|
| Bandit | 1.7.9 | Python SAST | 76 |
| Safety | 2.3.5 | SCA (pip) | PyPI Advisory DB |
| Trivy | 0.52.0 | 容器扫描 | NVD + OSV |
| Semgrep | 1.102.0 | 语义分析 | 568 |

## 代码质量工具

| 工具 | 版本 | 用途 |
|------|------|------|
| radon | 5.1.0 | 复杂度分析 |
| cognitive_complexity | 2.0.0 | 认知复杂度 |
| pylint | 3.0.3 | 代码规范 |
| mccabe | 0.6.1 | 圈复杂度 |
| flake8 | 6.1.0 | 风格检查 |

## 测试工具

| 工具 | 版本 | 用途 |
|------|------|------|
| pytest | 7.4.3 | 单元测试 |
| pytest-benchmark | 4.0.0 | 性能基准 |
| coverage | 7.3.2 | 覆盖率分析 |
| locust | 2.20.1 | 负载测试 |

## 基础设施工具

| 工具 | 版本 | 用途 |
|------|------|------|
| docker-compose | 2.23.3 | 容器编排 |
| open-telemetry | 1.22.0 | 可观测性 |
| matrix-synapse | 1.107.0 | 通信层 |
| higress | 2.1.0 | AI 网关 |

## 依赖管理

| 类别 | 数量 | 许可证 |
|------|------|--------|
| pip 包 | 156 | Apache 2.0 (89%), MIT (11%) |
| npm 包 | 0 | N/A |
| Docker 镜像 | 8 | 全部基础镜像安全扫描通过 |

## 版本锁定

所有工具版本已在 `requirements.txt` 和 `docker-compose.yml` 中锁定，确保审计可复现。

```
# requirements.txt 关键依赖
bandit==1.7.9
safety==2.3.5
trivy-container-scanner==0.52.0
semgrep==1.102.0
radon==5.1.0
pylint==3.0.3
mccabe==0.6.1
pytest==7.4.3
pytest-benchmark==4.0.0
coverage==7.3.2
locust==2.20.1
```
