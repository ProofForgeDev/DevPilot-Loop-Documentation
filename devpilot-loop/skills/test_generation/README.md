# DevPilot Loop — ${skill} Skill

## 概述
${skill} Skill 是 DevPilot Loop 的核心可复用模块，提供标准化的代码分析和处理功能。

## 安装
```bash
pip install -e .
```

## 使用
```python
from skills.${skill//_/}.skill import ${skill//_/}Skill

skill = ${skill//_/}Skill()
result = skill.execute({"source_code": "your code here"})
```

## 接口
- `execute(input_data)` — 执行分析，返回结构化结果
- `validate_input(input_data)` — 校验输入格式
- `get_schema()` — 返回 JSON Schema

## 测试
```bash
python -m pytest skills/${skill}/tests/ -v
```
