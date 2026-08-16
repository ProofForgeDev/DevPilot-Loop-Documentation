"""LLM 配置管理"""
import os
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM 网关配置"""
    provider: str = "openai-compatible"
    endpoint: str = os.getenv("LLM_ENDPOINT", "http://higress:8080/v1/chat/completions")
    model_name: str = os.getenv("LLM_MODEL", "qwen-max")
    api_key: str = os.getenv("LLM_API_KEY", "")
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 60
    
    # 降级配置
    fallback_to_rules: bool = True
    cache_enabled: bool = True
