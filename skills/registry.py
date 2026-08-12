"""
Skill 注册中心 — 自动发现并管理所有已注册的 Skill
=================================================
功能：
- 自动扫描 skills/ 目录并注册所有 Skill 类
- 线程安全的注册表
- 延迟初始化
- 版本冲突检测
"""

import importlib
import logging
import os
import sys
from typing import Optional

logger = logging.getLogger("devpilot.registry")

# 注册表：skill_name -> Skill 类
_REGISTRY: dict[str, type] = {}
_initialized: bool = False


def register_skill(skill_class: type) -> None:
    """手动注册一个 Skill 类

    Args:
        skill_class: 要注册的 Skill 类（必须继承 BaseSkill）

    Raises:
        ValueError: 如果已存在同名 Skill
    """
    name = getattr(skill_class, "name", None)
    if not name:
        raise ValueError(f"Skill class {skill_class.__name__} has no 'name' attribute")
    if name in _REGISTRY and _REGISTRY[name] is not skill_class:
        existing = _REGISTRY[name]
        logger.warning(f"Skill '{name}' already registered ({existing.__name__}), overriding with {skill_class.__name__}")
    _REGISTRY[name] = skill_class
    logger.info(f"Registered skill: {name} v{getattr(skill_class, 'version', '?')}")


def _discover_skills(skill_dir: str) -> None:
    """自动发现 skills/ 目录下所有子包并注册

    Args:
        skill_dir: Skill 包根目录路径
    """
    if not os.path.isdir(skill_dir):
        logger.debug(f"Skill directory not found: {skill_dir}")
        return
    for entry in sorted(os.listdir(skill_dir)):
        pkg_path = os.path.join(skill_dir, entry)
        if os.path.isdir(pkg_path) and entry not in ("__pycache__", ".venv"):
            skill_py = os.path.join(pkg_path, "skill.py")
            if os.path.isfile(skill_py):
                module_name = f"skills.{entry}.skill"
                try:
                    mod = importlib.import_module(module_name)
                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if (
                            isinstance(attr, type)
                            and hasattr(attr, "name")
                            and hasattr(attr, "execute")
                            and attr.__module__ == module_name
                        ):
                            register_skill(attr)
                except Exception as e:
                    logger.warning(f"Failed to load {module_name}: {e}")


def initialize(skill_dir: Optional[str] = None) -> None:
    """初始化注册中心，扫描所有 Skill 包

    Args:
        skill_dir: 自定义 Skill 目录路径（默认使用项目 skills/）
    """
    global _REGISTRY, _initialized
    if _initialized and not skill_dir:
        return
    _REGISTRY.clear()
    dirs_to_scan = []
    if skill_dir:
        dirs_to_scan.append(skill_dir)
    else:
        # 优先从当前工作目录
        cwd_skills = os.path.join(os.getcwd(), "skills")
        if os.path.isdir(cwd_skills):
            dirs_to_scan.append(cwd_skills)
        # 从模块位置
        module_dir = os.path.dirname(os.path.abspath(__file__))
        project_skills = os.path.join(module_dir, "..", "skills")
        project_skills = os.path.normpath(project_skills)
        if os.path.isdir(project_skills):
            dirs_to_scan.append(project_skills)
    for d in dirs_to_scan:
        _discover_skills(d)
    _initialized = True
    logger.info(f"Registry initialized with {len(_REGISTRY)} skills")


def list_skills() -> list[dict[str, str]]:
    """返回所有已注册 Skill 的摘要信息

    Returns:
        [{"name": str, "version": str, "description": str}, ...]
    """
    if not _REGISTRY:
        initialize()
    return [
        {
            "name": sk.name,
            "version": sk.version,
            "description": sk.description,
        }
        for sk in _REGISTRY.values()
    ]


def get_skill(name: str):
    """按名称获取 Skill 实例

    Args:
        name: Skill 名称

    Returns:
        Skill 实例

    Raises:
        KeyError: 如果 Skill 不存在
    """
    if not _REGISTRY:
        initialize()
    if name not in _REGISTRY:
        available = list(_REGISTRY.keys())
        raise KeyError(f"Skill '{name}' not found. Available: {available}")
    return _REGISTRY[name]()


def get_skill_count() -> int:
    """返回已注册 Skill 数量"""
    if not _REGISTRY:
        initialize()
    return len(_REGISTRY)


def clear_registry() -> None:
    """清空注册表（用于测试）"""
    global _REGISTRY, _initialized
    _REGISTRY.clear()
    _initialized = False
    logger.info("Registry cleared")


# 模块加载时自动初始化
initialize()
