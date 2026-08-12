# ============================================================
# HiClaw Runtime — 最小化兼容框架
# ============================================================
# nicepkg/hiclaw 仓库不可用（HTTP 404），本目录提供 HiClaw
# API 兼容的最小运行时，支持 Manager-Worker 通信和 Skill 调用。
#
# 参考: https://github.com/agentscope-ai/AgentTeams (5377+ Stars)
# 本运行时模拟 HiClaw HTTP API 以支持本地 PoC 验证。
#
# 构建上下文: 从 poc/deploy/ 运行 docker compose build
#             context: .. 解析到 poc/ 目录
#             COPY 路径相对于 poc/，即 deploy/runtime/...
# ============================================================

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl jq procps \
    && rm -rf /var/lib/apt/lists/*

# 安装轻量 HTTP 框架（用于 Agent 间通信模拟）
RUN pip install --no-cache-dir fastapi uvicorn httpx pyyaml

WORKDIR /app

# 复制运行时脚本（相对于 poc/ 上下文）
COPY deploy/runtime/agent_runtime.py /app/agent_runtime.py
COPY deploy/runtime/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# 挂载 Agent 配置目录
VOLUME ["/app/agent"]

EXPOSE 8001

# uvicorn 直接使用 app 对象，通过环境变量 AGENT_TYPE 区分 Manager/Worker 行为
ENTRYPOINT ["python", "-m", "uvicorn", "agent_runtime:app", \
            "--host", "0.0.0.0", "--port", "8001"]
