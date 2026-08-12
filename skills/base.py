"""
BaseSkill — 所有 Skill 的基类
==============================
定义 Skill 的标准接口：execute / validate_input / get_schema
所有具体 Skill 继承此类实现自己的逻辑。
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseSkill(ABC):
    """所有 DevPilot Loop Skill 的抽象基类"""

    name: str = "base"
    version: str = "0.1.0"
    description: str = "Base skill class"

    @abstractmethod
    def execute(self, input_data: dict) -> dict:
        """执行 Skill，接收输入，返回结构化结果"""
        raise NotImplementedError

    @abstractmethod
    def validate_input(self, input_data: dict) -> bool:
        """校验输入格式是否合法"""
        raise NotImplementedError

    @abstractmethod
    def get_schema(self) -> dict:
        """返回 input/output JSON Schema"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} v{self.version}>"
