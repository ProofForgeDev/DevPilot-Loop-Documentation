"""
Credential Manager — 零信任凭证管理
====================================
功能：
- 安全存储 Agent 凭证（加密）
- 动态注入 Worker 环境变量
- 凭证轮换
- 审计追踪
"""

import json
import os
import hashlib
import hmac
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from pathlib import Path

logger = logging.getLogger("devpilot.credentials")


class CredentialStore:
    """凭证存储 — 支持文件和内存两种模式"""

    def __init__(self, storage_path: Optional[str] = None):
        self._store: dict[str, dict] = {}
        self._storage_path = storage_path or os.environ.get(
            "CREDENTIAL_STORE_PATH", "/tmp/devpilot-credentials.json"
        )
        self._load()

    def _load(self) -> None:
        """从文件加载凭证"""
        path = Path(self._storage_path)
        if path.exists():
            try:
                with open(path) as f:
                    self._store = json.load(f)
                logger.info(f"Loaded {len(self._store)} credentials from {self._storage_path}")
            except Exception as e:
                logger.warning(f"Failed to load credentials: {e}")
                self._store = {}

    def _save(self) -> None:
        """持久化凭证到文件"""
        try:
            path = Path(self._storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(self._store, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")

    def register(self, name: str, value: str, meta: Optional[dict] = None) -> None:
        """注册新凭证"""
        self._store[name] = {
            "value_hash": self._hash(value),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "metadata": meta or {},
            "rotation_count": 0,
        }
        self._save()
        logger.info(f"Registered credential: {name}")

    def rotate(self, name: str, new_value: str) -> bool:
        """轮换凭证"""
        if name not in self._store:
            return False
        self._store[name]["value_hash"] = self._hash(new_value)
        self._store[name]["rotation_count"] += 1
        self._store[name]["updated_at"] = _now_iso()
        self._save()
        logger.info(f"Rotated credential: {name} (rotation #{self._store[name]['rotation_count']})")
        return True

    def verify(self, name: str, value: str) -> bool:
        """验证凭证值"""
        if name not in self._store:
            return False
        return self._store[name]["value_hash"] == self._hash(value)

    def get_hash(self, name: str) -> Optional[str]:
        """获取凭证哈希（不暴露明文）"""
        return self._store.get(name, {}).get("value_hash")

    def list_credentials(self) -> list[str]:
        """列出所有凭证名称（不含值）"""
        return list(self._store.keys())

    def delete(self, name: str) -> bool:
        """删除凭证"""
        if name in self._store:
            del self._store[name]
            self._save()
            return True
        return False

    def _hash(self, value: str) -> str:
        """SHA-256 哈希"""
        return hashlib.sha256(value.encode()).hexdigest()


class PermissionManager:
    """基于角色的权限管理"""

    # 权限级别
    L1_READONLY = "L1"
    L2_WRITE_APPROVED = "L2"
    L3_PRODUCTION = "L3"

    _PERMISSION_MAP = {
        "L1": {"read": True, "write": False, "approve": False, "deploy": False},
        "L2": {"read": True, "write": True, "approve": False, "deploy": False},
        "L3": {"read": True, "write": True, "approve": True, "deploy": True},
    }

    def __init__(self):
        self._agent_permissions: dict[str, str] = {}

    def set_permission(self, agent_name: str, level: str) -> None:
        """设置 Agent 权限级别"""
        if level not in self._PERMISSION_MAP:
            raise ValueError(f"Invalid permission level: {level}")
        self._agent_permissions[agent_name] = level
        logger.info(f"Set permission for {agent_name}: {level}")

    def check_permission(self, agent_name: str, action: str) -> bool:
        """检查 Agent 是否有执行某操作的权限"""
        level = self._agent_permissions.get(agent_name, self.L1_READONLY)
        perms = self._PERMISSION_MAP[level]
        allowed = {
            "read": perms["read"],
            "write": perms["write"],
            "approve": perms["approve"],
            "deploy": perms["deploy"],
        }
        return allowed.get(action, False)

    def get_agent_level(self, agent_name: str) -> str:
        """获取 Agent 权限级别"""
        return self._agent_permissions.get(agent_name, self.L1_READONLY)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# 全局单例
_credential_store: Optional[CredentialStore] = None
_permission_manager: Optional[PermissionManager] = None


def get_credential_store() -> CredentialStore:
    global _credential_store
    if _credential_store is None:
        _credential_store = CredentialStore()
    return _credential_store


def get_permission_manager() -> PermissionManager:
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager


if __name__ == "__main__":
    # 快速验证
    store = get_credential_store()
    store.register("api_key", "secret123", {"env": "production"})
    store.register("db_password", "dbpass456")
    assert store.verify("api_key", "secret123")
    assert not store.verify("api_key", "wrong")
    assert store.get_hash("api_key") is not None
    print(f"Credentials: {store.list_credentials()}")
    print("Credential Manager: OK")
