"""
Tests for OrchestratorSkill — 任务编排测试
============================================="""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.orchestrator import OrchestratorSkill


@pytest.fixture
def skill():
    return OrchestratorSkill()


def test_idempotent(skill):
    assert skill.name == "orchestrator"
    assert skill.version == "2.0.0"


def test_sequential_execution(skill):
    tasks = [
        {"id": "t1", "skill": "code-review", "payload": {"source_code": "x=1"}},
        {"id": "t2", "skill": "security-scan", "payload": {"source_code": "x=2"}},
    ]
    result = skill.execute({"tasks": tasks})
    assert result["status"] == "ok"
    assert result["completed_tasks"] == 2
    assert result["failed_tasks"] == 0
    assert result["strategy"] == "sequential"


def test_parallel_execution(skill):
    tasks = [{"id": f"t{i}", "skill": "code-review", "payload": {"source_code": f"x={i}"}}
             for i in range(3)]
    result = skill.execute({"tasks": tasks, "strategy": "parallel"})
    assert result["completed_tasks"] == 3
    assert result["strategy"] == "parallel"


def test_pipeline_execution(skill):
    tasks = [{"id": f"t{i}", "skill": "doc-writing", "payload": {"doc_type": "api", "title": f"Doc {i}"}}
             for i in range(2)]
    result = skill.execute({"tasks": tasks, "strategy": "pipeline"})
    assert result["completed_tasks"] == 2


def test_empty_tasks(skill):
    result = skill.execute({"tasks": []})
    assert result["status"] == "ok"


def test_single_task(skill):
    tasks = [{"id": "t1", "skill": "test-generation", "payload": {"source_code": "def f(): pass"}}]
    result = skill.execute({"tasks": tasks})
    assert result["total_tasks"] == 1
    assert result["completed_tasks"] == 1


def test_result_structure(skill):
    tasks = [{"id": "t1", "skill": "code-review", "payload": {"source_code": "x=1"}}]
    result = skill.execute({"tasks": tasks})
    assert "results" in result
    assert len(result["results"]) == 1
    r = result["results"][0]
    assert "task_id" in r
    assert "skill" in r
    assert "phase" in r


def test_max_retries(skill):
    tasks = [{"id": "t1", "skill": "code-review", "payload": {"source_code": "x=1"}}]
    result = skill.execute({"tasks": tasks, "max_retries": 5})
    assert result["status"] == "ok"


def test_validate_input_valid(skill):
    assert skill.validate_input({"tasks": [{"id": "t1", "skill": "a", "payload": {}}]}) is True


def test_validate_input_empty(skill):
    assert skill.validate_input({"tasks": []}) is False


def test_validate_input_missing_tasks(skill):
    assert skill.validate_input({}) is False


def test_validate_input_not_dict(skill):
    assert skill.validate_input("not a dict") is False
    assert skill.validate_input(None) is False


def test_get_schema(skill):
    schema = skill.get_schema()
    assert "input" in schema
    assert "output" in schema
    assert "tasks" in schema["input"]["required"]


def test_results_match_input_count(skill):
    tasks = [{"id": f"t{i}", "skill": "code-review", "payload": {"source_code": "x=1"}}
             for i in range(5)]
    result = skill.execute({"tasks": tasks})
    assert len(result["results"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
