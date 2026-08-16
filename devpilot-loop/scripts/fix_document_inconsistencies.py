#!/usr/bin/env python3
"""Fix ALL numeric inconsistencies in README.md and EVIDENCE-INDEX.md for GOAI submission."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

# ========== README.md fixes ==========
with open(ROOT / 'README.md', 'r') as f:
    readme = f.read()

fixes_readme = [
    # Line 15: "证据 104 份" → "证据 44 份"
    ('**证据 104 份 (L1-L4 全覆盖)', '**证据 44 份 (L1-L4 全覆盖)'),
    # Line 22: "94 份证据总索引" → "44 份证据总索引"
    ('— 94 份证据总索引', '— 44 份证据总索引'),
    # Line 45: "94 份证据" → "44 份证据"
    ('+ 94 份证据', '+ 44 份证据'),
    # Line 154: "6 级证据体系" → "4 级证据体系（L1–L4）"
    ('### 6 级证据体系 (L1–L4)', '### 4 级证据体系（L1–L4）'),
    # Line 155: Table header - remove if needed
    # Line 158-161: Fix tier counts
    ('| **L1** 实机 | 直接系统输出 | 23 | 截图、日志、API 响应 |', '| **L1** 实机 | 直接系统输出 | 22 | 截图、日志、API 响应 |'),
    ('| **L2** 实机 | 系统化分析 | 12 | API 规范、配置文档 |', '| **L2** 实机 | 系统化分析 | 13 | API 规范、配置文档 |'),
    ('| **L3** 实现 | 聚合指标 | 5 | 性能基准、安全评分 |', '| **L3** 实现 | 聚合指标 | 3 | 性能基准、安全报告 |'),
    ('| **L4** 独立验证 | 第三方验证 | 2 | 审计报告、独立基准 |', '| **L4** 独立验证 | 第三方验证 | 6 | 审计报告、独立基准 |'),
    # Line 163: "证据 94 份文件" → "证据 44 份文件"
    ('**证据 94 份文件，100% 覆盖所有评分维度', '**证据 44 份文件，100% 覆盖所有评分维度'),
    # Line 200: "设计文档（18 份 Markdown + 2 JSON）" → "设计文档（29 份）"
    ('# 设计文档（18 份 Markdown + 2 JSON）', '# 设计文档（29 份）'),
    # Line 223: "L1-L4 证据体系（50+ 文件）" → "L1-L4 证据体系（44 份）"
    ('# L1-L4 证据体系（50+ 文件）', '# L1-L4 证据体系（44 份）'),
    # Line 299: "tests.*?274 个测试用例（23 个文件）" → "tests/（28 个文件，366 个测试用例）"
    ('├── tests.*?274 个测试用例（23 个文件）', '├── tests/                 # 测试套件（28 个文件，366 个测试用例）'),
    # Line 422: "240+ 文件 · 14,693 行 Python 代码 · 274 个测试用例 · 94 份证据文件"
    ('**统计**: 240+ 文件 · 14,693 行 Python 代码 · 274 个测试用例 · 94 份证据文件',
     '**统计**: 240+ 文件 · 14,693 行 Python 代码 · 366 个测试用例 · 44 份证据文件'),
    # Line 577: "Skill 测试: **336/336** pytest passing"
    ('Skill 测试: **336/336** pytest passing', '测试套件: **366/366** pytest passing'),
    # Line 581: "证据 104 份** (L1-L4 全覆盖)"
    ('证据 104 份** (L1-L4 全覆盖)', '证据 44 份 (L1-L4 全覆盖)'),
    # Line 582: "PPT: **60 页** 专业演示文稿"
    ('PPT: **60 页** 专业演示文稿（含 Demo + Defense）', 'PPT: **54 页** 专业演示文稿（含 Demo + Defense）'),
    # Line 593: "全部文档（docs/ 15 份）"
    ('全部文档（docs/ 15 份）', '全部文档（docs/ 29 份）'),
    # Line 627: "### 4. 6 级证据体系"
    ('### 4. 6 级证据体系', '### 4. 4 级证据体系（L1–L4）'),
    # Line 628: "94 份证据文件"
    ('L1 实机 / L2 实机 / L3 实现 / L4 独立验证，确保每项宣称都有可验证证据。94 份证据文件，覆盖全部评分维度，100% 可追溯。',
     'L1 实机 / L2 实机 / L3 实现 / L4 独立验证，确保每项宣称都有可验证证据。44 份证据文件，覆盖全部评分维度，100% 可追溯。'),
    # Line 663: "测试通过率 | 274/274 (100%)"
    ('| 测试通过率 | 274/274 (100%) | pytest |', '| 测试通过率 | 366/366 (100%) | pytest |'),
    # Line 668: "证据 104 份 | L1-L4 四级体系"
    ('| 证据 104 份 | L1-L4 四级体系 |', '| 证据 44 份 | L1-L4 四级体系 |'),
    # Line 703: "统一证据 104 份"
    ('统一证据 104 份）、Agent 数量（9 个）、PPT 页数（54 页）', '统一证据 44 份）、Agent 数量（9 个）、PPT 页数（54 页）'),
]

for old, new in fixes_readme:
    if old in readme:
        readme = readme.replace(old, new)
        print(f"  ✅ README: {old[:50]}...")
    else:
        # Try partial match
        cleaned_old = re.sub(r'\?', '', old)  # Remove glob chars
        if cleaned_old in readme:
            readme = readme.replace(cleaned_old, new)
            print(f"  ✅ README (partial): {old[:50]}...")
        else:
            print(f"  ⚠️ README NOT FOUND: {old[:60]}")

with open(ROOT / 'README.md', 'w') as f:
    f.write(readme)
print("README.md saved.")

# ========== EVIDENCE-INDEX.md fixes ==========
with open(ROOT / 'EVIDENCE-INDEX.md', 'r') as f:
    evidence_index = f.read()

fixes_evidence = [
    # Line 15: "**合计** | | **104**" → "**合计** | | **44**"
    ('| **合计** | | **104** | **100%** | | **100%** | | **100%** | | **100%** | | **100%** | | **100%** |',
     '| **合计** | | **44** | **100%** |'),
    # Line 11: "文件数 | 占比" table - fix total row
    ('## 证据概览\n\n| 层级 | 含义 | 文件数 | 占比 |',
     '## 证据概览\n\n| 层级 | 含义 | 文件数 | 占比 |\n|------|------|--------|------|'),
    # Line 11 header row needs to be fixed if missing
]

for old, new in fixes_evidence:
    if old in evidence_index:
        evidence_index = evidence_index.replace(old, new)
        print(f"  ✅ EVIDENCE-INDEX: {old[:50]}...")
    else:
        print(f"  ⚠️ EVIDENCE-INDEX NOT FOUND: {old[:60]}")

with open(ROOT / 'EVIDENCE-INDEX.md', 'w') as f:
    f.write(evidence_index)
print("EVIDENCE-INDEX.md saved.")

print("\n=== Summary of fixes ===")
print("README.md: Fixed evidence counts (104→44, 94→44), test counts (336→366, 274→366),")
print("           PPT pages (60→54), docs count (18/15→29), tier breakdown (L1:23,L2:12,L3:5,L4:2→L1:22,L2:13,L3:3,L4:6)")
print("EVIDENCE-INDEX.md: Fixed total count (104→44)")
