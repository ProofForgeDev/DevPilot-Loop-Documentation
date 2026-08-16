"""
DevPilot Loop — AgentTeams (HiClaw) SDK Integration
=====================================================
提供与 AgentTeams 框架兼容的接口实现。
支持 Manager-Worker 架构、Skill 注册、消息路由。
"""

from .manager import AgentManager
from .worker import AgentWorker
from .registry import SkillRegistry
from .message import MessageBus

__version__ = "2.2.0"
__all__ = ['AgentManager', 'AgentWorker', 'SkillRegistry', 'MessageBus']
