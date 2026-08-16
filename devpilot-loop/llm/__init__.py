"""
DevPilot Loop — LLM Gateway Adapter
=====================================
统一 LLM 调用接口，支持多种后端：
- OpenAI compatible (OpenRouter, local Ollama, etc.)
- 本地规则引擎（无 LLM 时的降级方案）
- 批量请求缓存（减少 API 调用成本）
"""

from .adapter import LLMAdapter, create_adapter
from .config import LLMConfig

__all__ = ['LLMAdapter', 'create_adapter', 'LLMConfig']
