"""Skill 注册中心 — 自动发现并管理所有已注册的 Skill"""

import importlib
import os
import sys
from typing import Optional

# 注册表：skill_name -> Skill 类
_REGISTRY: dict = {}


def register_skill(skill_class) -> None:
    """手动注册一个 Skill 类"""
    _REGISTRY[skill_class.name] = skill_class


def _discover_skills(skill_dir: str) -> None:
    """自动发现 skills/ 目录下所有子包并注册"""
    if not os.path.isdir(skill_dir):
        return
    for entry in sorted(os.listdir(skill_dir)):
        pkg_path = os.path.join(skill_dir, entry)
        if os.path.isdir(pkg_path) and entry not in ("__pycache__",):
            init_py = os.path.join(pkg_path, "skill.py")
            if os.path.isfile(init_py):
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
                    print(f"  [WARN] Failed to load {module_name}: {e}", file=sys.stderr)


def initialize() -> None:
    """初始化注册中心，扫描 skills/ 目录"""
    _REGISTRY.clear()
    # 优先从当前工作目录的 skills/ 加载
    skill_dir = os.path.join(os.getcwd(), "skills")
    if not os.path.isdir(skill_dir):
        skill_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")
    _discover_skills(skill_dir)
    # 也尝试从包路径加载
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    _discover_skills(pkg_dir)


def list_skills() -> list:
    """返回所有已注册 Skill 的摘要信息"""
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
    """按名称获取 Skill 实例"""
    if not _REGISTRY:
        initialize()
    if name not in _REGISTRY:
        raise KeyError(f"Skill '{name}' not found. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]()


def get_skill_count() -> int:
    if not _REGISTRY:
        initialize()
    return len(_REGISTRY)


# 模块加载时自动初始化
initialize()
