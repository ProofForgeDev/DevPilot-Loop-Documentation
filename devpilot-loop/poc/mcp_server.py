"""
MCP (Model Context Protocol) Server Implementation
===================================================
本模块提供 MCP 协议兼容的工具服务，实现以下工具：
1. issue_tracker - Issue Tracker 查询
2. git_ops - Git 仓库操作（读代码、commit history）
3. test_runner - 测试执行
4. knowledge_base - 知识库检索

所有工具调用通过 Higress AI 网关路由，凭证由网关注入。
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("devpilot.mcp")

# MCP Protocol Constants
MCP_VERSION = "2024-11-05"
JSONRPC_VERSION = "2.0"


class MCPServer:
    """MCP Server 实现 - 提供工具调用接口"""
    
    def __init__(self):
        self.tools = {
            "issue_tracker": {
                "name": "issue_tracker",
                "description": "查询 Issue Tracker 中的缺陷、需求、告警",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "get", "search"]},
                        "project_id": {"type": "string"},
                        "filter": {"type": "object"},
                        "limit": {"type": "integer", "default": 20},
                        "cursor": {"type": "string"}
                    },
                    "required": ["action"]
                }
            },
            "git_ops": {
                "name": "git_ops",
                "description": "Git 仓库操作：读取代码、commit history、branch 管理",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["read_file", "list_commits", "create_branch", "get_diff"]},
                        "repo_path": {"type": "string"},
                        "file_path": {"type": "string"},
                        "commit_range": {"type": "string"}
                    },
                    "required": ["action", "repo_path"]
                }
            },
            "test_runner": {
                "name": "test_runner",
                "description": "执行测试套件，返回测试结果和覆盖率报告",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "test_suite": {"type": "string"},
                        "test_path": {"type": "string"},
                        "coverage": {"type": "boolean", "default": True}
                    },
                    "required": ["test_suite"]
                }
            },
            "knowledge_base": {
                "name": "knowledge_base",
                "description": "检索知识库（Runbook、FAQ、历史缺陷记录）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "default": 5},
                        "category": {"type": "string", "enum": ["runbook", "faq", "defect", "all"]}
                    },
                    "required": ["query"]
                }
            }
        }
        self._call_log: List[Dict[str, Any]] = []
    
    def list_tools(self) -> Dict[str, Any]:
        """返回所有可用工具列表"""
        return {
            "tools": list(self.tools.keys()),
            "tool_schemas": self.tools
        }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具并返回结果"""
        call_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # 记录调用日志
        call_record = {
            "call_id": call_id,
            "timestamp": timestamp,
            "tool": tool_name,
            "arguments": arguments,
            "status": "pending"
        }
        
        # 执行工具调用（本地网关模式）
        result = self._simulate_tool_execution(tool_name, arguments)
        
        call_record["status"] = "success" if result.get("isError") is not True else "error"
        call_record["result"] = result
        self._call_log.append(call_record)
        
        logger.info(f"MCP tool call: {tool_name} (call_id={call_id})")
        
        return result
    
    def _simulate_tool_execution(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用（本地网关模式）"""
        if tool_name == "issue_tracker":
            action = arguments.get("action", "list")
            if action == "list":
                return {
                    "content": [{"type": "text", "text": json.dumps({
                        "issues": [
                            {"id": "BUG-001", "title": "Login NPE", "status": "open", "priority": "P1"},
                            {"id": "BUG-002", "title": "Payment timeout", "status": "open", "priority": "P0"}
                        ],
                        "total": 2
                    })}],
                    "isError": False
                }
        
        elif tool_name == "git_ops":
            action = arguments.get("action", "read_file")
            if action == "read_file":
                return {
                    "content": [{"type": "text", "text": "# Sample code file\n\ndef login(username, password):\n    if username is None:\n        raise ValueError('username cannot be None')\n    return authenticate(username, password)"}],
                    "isError": False
                }
        
        elif tool_name == "test_runner":
            return {
                "content": [{"type": "text", "text": json.dumps({
                    "total": 100,
                    "passed": 98,
                    "failed": 2,
                    "skipped": 0,
                    "coverage": 95.2
                })}],
                "isError": False
            }
        
        elif tool_name == "knowledge_base":
            return {
                "content": [{"type": "text", "text": json.dumps({
                    "results": [
                        {"title": "NPE in login module", "category": "defect", "similarity": 0.95},
                        {"title": "Login authentication runbook", "category": "runbook", "similarity": 0.87}
                    ]
                })}],
                "isError": False
            }
        
        return {
            "content": [{"type": "text", "text": "Unknown tool or action"}],
            "isError": True
        }
    
    def get_call_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """返回最近的工具调用历史"""
        return self._call_log[-limit:]


# 全局 MCP Server 实例
mcp_server = MCPServer()


def get_mcp_tools() -> Dict[str, Any]:
    """返回 MCP 工具列表（供 Agent 调用）"""
    return mcp_server.list_tools()


def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """调用 MCP 工具（供 Agent 调用）"""
    return mcp_server.call_tool(tool_name, arguments)
