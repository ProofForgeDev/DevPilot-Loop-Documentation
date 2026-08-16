"""
Security Unit Tests — 凭证安全单元测试
======================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from poc.security.credential_manager import CredentialStore, PermissionManager


def test_credential_hashing():
    """Test SHA-256 hashing of credentials"""
    store = CredentialStore()
    hashed = store._hash("test-secret")
    assert len(hashed) == 64  # SHA-256 produces 64 hex chars
    assert hashed != "test-secret"


def test_store_and_retrieve():
    """Test store and retrieve credentials"""
    store = CredentialStore()
    store.register("service1", "secret1")
    retrieved = store.get_hash("service1")
    assert retrieved is not None
    assert len(retrieved) == 64


def test_verify_credential():
    """Test credential verification"""
    store = CredentialStore()
    store.register("svc", "my-secret")
    assert store.verify("svc", "my-secret") is True
    assert store.verify("svc", "wrong-secret") is False


def test_missing_credential():
    """Test retrieving missing credential"""
    store = CredentialStore()
    result = store.get_hash("nonexistent")
    assert result is None


def test_overwrite_credential():
    """Test overwriting existing credential"""
    store = CredentialStore()
    store.register("service", "original")
    store.register("service", "updated")
    assert store.verify("service", "updated") is True
    assert store.verify("service", "original") is False


def test_empty_credential():
    """Test empty credential handling"""
    store = CredentialStore()
    hashed = store._hash("")
    assert len(hashed) == 64


def test_unicode_credential():
    """Test Unicode credential"""
    store = CredentialStore()
    secret = "密码-تسجيل-секрет"
    store.register("unicode-svc", secret)
    assert store.verify("unicode-svc", secret) is True


def test_large_credential():
    """Test large credential"""
    store = CredentialStore()
    secret = "x" * 10000
    store.register("large-svc", secret)
    assert store.verify("large-svc", secret) is True


def test_hash_consistency():
    """Test that same input produces same hash"""
    store = CredentialStore()
    secret = "consistent-test"
    hash1 = store._hash(secret)
    hash2 = store._hash(secret)
    assert hash1 == hash2


def test_permission_manager():
    """Test permission manager"""
    pm = PermissionManager()
    pm.set_permission("admin", "L3")
    pm.set_permission("worker", "L1")
    assert pm.get_agent_level("admin") == "L3"
    assert pm.get_agent_level("worker") == "L1"


def test_permission_check():
    """Test permission checking"""
    pm = PermissionManager()
    pm.set_permission("dev", "L2")
    assert pm.check_permission("dev", "deploy") is False  # L2 can't deploy
    assert pm.check_permission("dev", "write") is True     # L2 can write
    assert pm.check_permission("dev", "read") is True      # L2 can read


def test_credential_list():
    """Test listing credentials"""
    store = CredentialStore()
    store.register("svc-a", "secret-a")
    store.register("svc-b", "secret-b")
    creds = store.list_credentials()
    assert "svc-a" in creds
    assert "svc-b" in creds


def test_delete_credential():
    """Test deleting credentials"""
    store = CredentialStore()
    store.register("temp-svc", "temp-secret")
    assert store.delete("temp-svc") is True
    assert store.get_hash("temp-svc") is None


def test_rotate_credential():
    """Test credential rotation"""
    store = CredentialStore()
    store.register("app", "old-secret")
    assert store.rotate("app", "new-secret") is True
    assert store.verify("app", "new-secret") is True
    assert store.verify("app", "old-secret") is False


def test_meta_data_storage():
    """Test metadata storage with credentials"""
    store = CredentialStore()
    store.register("db-service", "db-pass", {"owner": "team-a", "created": "2024-01-01"})
    creds = store.list_credentials()
    assert "db-service" in creds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
