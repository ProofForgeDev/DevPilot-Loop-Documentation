"""测试生成 Skill — test-generation (Deep)
=============================================
根据源代码自动生成单元测试，支持多种测试类型和断言策略。
"""

from skills.base import BaseSkill
import re
from typing import Any


class TestGenerationSkill(BaseSkill):
    name = "test-generation"
    version = "2.0.0"
    description = "测试生成：单元/集成测试、边界值、异常路径、覆盖率分析"

    # 测试模式
    TEST_PATTERNS = {
        "unit": {
            "prefix": "test_",
            "style": "pytest",
            "imports": ["pytest"],
        },
        "integration": {
            "prefix": "test_integration_",
            "style": "pytest",
            "imports": ["pytest"],
        },
        "property": {
            "prefix": "test_property_",
            "style": "hypothesis",
            "imports": ["hypothesis", "given", "strategies"],
        },
    }

    def execute(self, input_data: dict) -> dict:
        source_code = input_data.get("source_code", "")
        test_type = input_data.get("test_type", "unit")
        file_path = input_data.get("file_path", "unknown")
        options = input_data.get("options", {})

        strict_mode = options.get("strict", False)
        generate_properties = options.get("generate_properties", False)
        include_fixtures = options.get("include_fixtures", True)
        coverage_target = options.get("coverage_target", 80)

        tests = []
        lines = source_code.splitlines()

        # 分析代码结构
        functions = self._extract_functions(lines)
        classes = self._extract_classes(lines)
        exceptions = self._detect_exceptions(lines)
        edge_cases = self._detect_edge_cases(lines, strict_mode)

        # 生成单元测试
        for func in functions:
            tests.extend(self._generate_function_tests(func, test_type, functions))

        for cls in classes:
            tests.extend(self._generate_class_tests(cls, test_type, classes))

        # 生成异常测试
        if exceptions:
            tests.extend(self._generate_exception_tests(exceptions, test_type))

        # 生成边界值测试
        if edge_cases:
            tests.extend(self._generate_edge_case_tests(edge_cases, test_type))

        # 生成属性测试
        if generate_properties:
            tests.extend(self._generate_property_tests(functions, test_type))

        # 生成 fixtures
        if include_fixtures:
            tests.extend(self._generate_fixtures(functions, classes))

        # 生成测试代码
        test_code = self._build_test_code(tests, test_type, options)

        # 覆盖率预估
        estimated_coverage = self._estimate_coverage(tests, lines)

        return {
            "skill": self.name,
            "version": self.version,
            "file": file_path,
            "tests_generated": len(tests),
            "coverage_target": coverage_target,
            "estimated_coverage": estimated_coverage,
            "tests": tests,
            "test_code": test_code,
            "summary": {
                "functions_tested": len([t for t in tests if t.get("target_type") == "function"]),
                "classes_tested": len([t for t in tests if t.get("target_type") == "class"]),
                "exception_tests": len([t for t in tests if t.get("type") == "exception"]),
                "edge_case_tests": len([t for t in tests if t.get("type") == "edge_case"]),
            },
            "status": "ok",
        }

    def _extract_functions(self, lines: list) -> list:
        """提取函数定义"""
        functions = []
        for i, line in enumerate(lines):
            match = re.match(r'^\s*def\s+(\w+)\s*\((.*?)\)\s*:', line)
            if match:
                name = match.group(1)
                params = match.group(2)
                functions.append({
                    "name": name,
                    "params": [p.strip().split('=')[0].split(':')[0].strip()
                               for p in params.split(',') if p.strip() and p.strip() != 'self'],
                    "line": i + 1,
                    "indent": len(line) - len(line.lstrip()),
                })
        return functions

    def _extract_classes(self, lines: list) -> list:
        """提取类定义"""
        classes = []
        for i, line in enumerate(lines):
            match = re.match(r'^\s*class\s+(\w+)', line)
            if match:
                classes.append({
                    "name": match.group(1),
                    "line": i + 1,
                    "indent": len(line) - len(line.lstrip()),
                })
        return classes

    def _detect_exceptions(self, lines: list) -> list:
        """检测异常处理"""
        exceptions = []
        for i, line in enumerate(lines):
            if 'raise ' in line or 'except ' in line:
                exceptions.append({"line": i + 1, "code": line.strip()})
        return exceptions

    def _detect_edge_cases(self, lines: list, strict: bool) -> list:
        """检测边界情况"""
        edge_cases = []
        for i, line in enumerate(lines):
            # 空值检查
            if 'is None' in line or 'is not None' in line or '== None' in line:
                edge_cases.append({"line": i + 1, "type": "null_check", "code": line.strip()})
            # 空字符串
            if '== ""' in line or '!= ""' in line or 'len(' in line:
                edge_cases.append({"line": i + 1, "type": "empty_string", "code": line.strip()})
            # 空列表
            if '== []' in line or '!= []' in line:
                edge_cases.append({"line": i + 1, "type": "empty_list", "code": line.strip()})
            # 类型检查
            if 'isinstance(' in line or 'type(' in line:
                edge_cases.append({"line": i + 1, "type": "type_check", "code": line.strip()})
        return edge_cases

    def _generate_function_tests(self, func: dict, test_type: str, all_functions: list) -> list:
        """生成函数测试用例"""
        tests = []
        prefix = "test_" if test_type == "unit" else "test_integration_"

        # 基本测试
        tests.append({
            "name": f"{prefix}{func['name']}_basic",
            "target": func["name"],
            "target_type": "function",
            "type": "unit",
            "description": f"Basic test for {func['name']}",
            "line": func["line"],
        })

        # 参数测试
        for param in func["params"]:
            if param != "self":
                tests.append({
                    "name": f"{prefix}{func['name']}_{param}_param",
                    "target": func["name"],
                    "target_type": "function",
                    "type": "parameter",
                    "description": f"Test {param} parameter for {func['name']}",
                    "line": func["line"],
                })

        # 返回值测试
        tests.append({
            "name": f"{prefix}{func['name']}_return",
            "target": func["name"],
            "target_type": "function",
            "type": "return_value",
            "description": f"Test return value for {func['name']}",
            "line": func["line"],
        })

        return tests

    def _generate_class_tests(self, cls: dict, test_type: str, all_classes: list) -> list:
        """生成类测试用例"""
        tests = []
        prefix = "test_" if test_type == "unit" else "test_integration_"
        class_prefix = f"Test{cls['name']}"

        tests.append({
            "name": f"{prefix}test_{cls['name'].lower()}_ instantiation",
            "target": cls["name"],
            "target_type": "class",
            "type": "instantiation",
            "description": f"Test instantiation of {cls['name']}",
            "line": cls["line"],
        })

        tests.append({
            "name": f"{prefix}test_{cls['name'].lower()}_methods",
            "target": cls["name"],
            "target_type": "class",
            "type": "methods",
            "description": f"Test methods of {cls['name']}",
            "line": cls["line"],
        })

        return tests

    def _generate_exception_tests(self, exceptions: list, test_type: str) -> list:
        """生成异常测试"""
        tests = []
        for exc in exceptions:
            tests.append({
                "name": f"test_{exc['type']}_at_line_{exc['line']}",
                "target": f"exception_handler",
                "target_type": "exception",
                "type": "exception",
                "description": f"Test exception handling at line {exc['line']}",
                "line": exc["line"],
            })
        return tests

    def _generate_edge_case_tests(self, edge_cases: list, test_type: str) -> list:
        """生成边界值测试"""
        tests = []
        for case in edge_cases:
            tests.append({
                "name": f"test_{case['type']}_edge_case",
                "target": "edge_cases",
                "target_type": "edge_case",
                "type": "edge_case",
                "description": f"Test {case['type']} edge case at line {case['line']}",
                "line": case["line"],
            })
        return tests

    def _generate_property_tests(self, functions: list, test_type: str) -> list:
        """生成属性测试"""
        tests = []
        for func in functions:
            tests.append({
                "name": f"test_property_{func['name']}_invariant",
                "target": func["name"],
                "target_type": "function",
                "type": "property",
                "description": f"Property-based test for {func['name']}",
                "line": func["line"],
            })
        return tests

    def _generate_fixtures(self, functions: list, classes: list) -> list:
        """生成测试 fixtures"""
        fixtures = []

        # 通用 fixture
        fixtures.append({
            "name": "sample_data",
            "type": "fixture",
            "description": "Sample test data",
        })

        # 类 fixture
        for cls in classes:
            fixtures.append({
                "name": f"{cls['name'].lower()}_instance",
                "type": "fixture",
                "description": f"Instance of {cls['name']}",
            })

        return fixtures

    def _build_test_code(self, tests: list, test_type: str, options: dict) -> str:
        """构建测试代码"""
        lines = [f'"""Generated tests for {test_type} testing"""']
        lines.append("import pytest")

        if options.get("generate_properties"):
            lines.append("from hypothesis import given, strategies as st")

        lines.append("")
        lines.append("")

        # 添加 fixtures
        if options.get("include_fixtures"):
            lines.append("# Fixtures")
            lines.append("@pytest.fixture")
            lines.append("def sample_data():")
            lines.append('    return {"key": "value"}')
            lines.append("")
            lines.append("")

        # 添加测试用例
        for test in tests[:20]:  # 限制输出数量
            test_name = test["name"]
            description = test["description"]

            lines.append(f"# {description}")
            lines.append(f"@pytest.mark.{test['type']}")
            lines.append(f"def test_{test_name.replace('test_', '')}():")
            lines.append('    pass  # TODO: Implement test logic')
            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def _estimate_coverage(self, tests: list, source_lines: list) -> float:
        """估算测试覆盖率"""
        if not source_lines:
            return 0.0

        # 基于测试数量估算
        test_count = len(tests)
        line_count = len(source_lines)
        ratio = test_count / max(line_count, 1)

        # 简单估算模型
        estimated = min(95, max(10, ratio * 100))
        return round(estimated, 1)

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and "source_code" in input_data

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "required": ["source_code"],
                "properties": {
                    "source_code": {"type": "string", "description": "源代码"},
                    "test_type": {"type": "string", "enum": ["unit", "integration", "property"], "default": "unit"},
                    "file_path": {"type": "string", "description": "文件路径（可选）"},
                    "options": {
                        "type": "object",
                        "properties": {
                            "strict": {"type": "boolean", "description": "严格模式"},
                            "generate_properties": {"type": "boolean", "description": "生成属性测试"},
                            "include_fixtures": {"type": "boolean", "description": "包含 fixtures"},
                            "coverage_target": {"type": "integer", "description": "覆盖率目标（%）"},
                        }
                    }
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "version": {"type": "string"},
                    "file": {"type": "string"},
                    "tests_generated": {"type": "integer"},
                    "coverage_target": {"type": "integer"},
                    "estimated_coverage": {"type": "number"},
                    "tests": {"type": "array"},
                    "test_code": {"type": "string"},
                    "summary": {"type": "object"},
                    "status": {"type": "string"},
                },
            },
        }
