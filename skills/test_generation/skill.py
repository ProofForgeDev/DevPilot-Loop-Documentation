"""测试生成 Skill — test-generation
====================================
根据源代码自动生成单元测试。
"""

from skills.base import BaseSkill


class TestGenerationSkill(BaseSkill):
    name = "test-generation"
    version = "1.0.0"
    description = "测试生成：根据源代码自动生成单元测试用例"

    def execute(self, input_data: dict) -> dict:
        source_code = input_data.get("source_code", "")
        test_type = input_data.get("test_type", "unit")
        file_path = input_data.get("file_path", "unknown")

        tests = []
        lines = source_code.splitlines()

        # 扫描函数和类定义
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("def ") and not stripped.startswith("def _"):
                func_name = stripped.split("(")[0].replace("def ", "")
                tests.append({
                    "type": test_type,
                    "target": func_name,
                    "line": i,
                    "suggested_test": f"def test_{func_name}(): ...",
                })
            elif stripped.startswith("class ") and not stripped.startswith("class Test"):
                class_name = stripped.split("(")[0].replace("class ", "").strip()
                tests.append({
                    "type": test_type,
                    "target": class_name,
                    "line": i,
                    "suggested_test": f"class Test{class_name}: ...",
                })

        # 生成测试骨架
        test_code = f'"""Generated tests for {file_path}"""\nimport unittest\n\n'
        for t in tests:
            test_code += f"# {t['suggested_test']}\n"

        return {
            "skill": self.name,
            "version": self.version,
            "file": file_path,
            "tests_generated": len(tests),
            "tests": tests,
            "test_code": test_code,
            "status": "ok",
        }

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and "source_code" in input_data

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "required": ["source_code"],
                "properties": {
                    "source_code": {"type": "string", "description": "源代码"},
                    "test_type": {"type": "string", "enum": ["unit", "integration"], "default": "unit"},
                    "file_path": {"type": "string", "description": "文件路径（可选）"},
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "tests_generated": {"type": "integer"},
                    "test_code": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
        }
