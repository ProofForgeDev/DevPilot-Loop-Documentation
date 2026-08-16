"""
BaseSkill — 所有 Skill 的基类
==============================
定义 Skill 的标准接口：execute / validate_input / get_schema
所有具体 Skill 继承此类实现自己的逻辑。

特征：
- 抽象方法强制实现
- 自动日志记录
- 输入校验
- 异常处理与重试
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("devpilot.skills")


class BaseSkill(ABC):
    """所有 DevPilot Loop Skill 的抽象基类"""

    name: str = "base"
    version: str = "0.1.0"
    description: str = "Base skill class"
    max_retries: int = 3
    timeout_seconds: int = 300

    def __init__(self) -> None:
        self._call_count: int = 0
        self._last_result: dict[str, Any] | None = None

    @abstractmethod
    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行 Skill 核心逻辑

        Args:
            input_data: 标准化输入数据

        Returns:
            包含 status, output, evidence, metrics 的结构化结果
        """
        raise NotImplementedError

    @abstractmethod
    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """校验输入格式是否合法

        Args:
            input_data: 待校验的输入数据

        Returns:
            True 如果输入合法，False 否则
        """
        raise NotImplementedError

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """返回 input/output JSON Schema

        Returns:
            {"input": {...}, "output": {...}} 字典
        """
        raise NotImplementedError

    def execute_with_retry(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """带重试的执行包装器"""
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                result = self.execute(input_data)
                elapsed = time.time() - start
                self._call_count += 1
                self._last_result = result
                logger.info(
                    f"Skill {self.name} executed in {elapsed:.3f}s "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                result.setdefault("metrics", {})["execution_time_seconds"] = round(elapsed, 3)
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Skill {self.name} attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    raise
                time.sleep(0.1 * attempt)  # 指数退避
        raise last_error  # type: ignore

    def get_stats(self) -> dict[str, Any]:
        """返回 Skill 统计信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "call_count": self._call_count,
            "last_result": self._last_result,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} v{self.version} calls={self._call_count}>"
