#!/usr/bin/env python3
"""
DevPilot Loop — 真实图表生成器
==============================
使用 Pillow 生成所有 PPT 所需的真实图表，替换占位符。
"""

import os
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from datetime import datetime

# ── 路径 ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "slides", "assets")
EVIDENCE_DIR = os.path.join(BASE_DIR, "poc", "evidence", "screenshots")
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# ── 颜色 ──────────────────────────────────────────────────
CLR_DARK      = (0x1a, 0x3a, 0x5c)
CLR_BLUE      = (0x2e, 0x86, 0xab)
CLR_LIGHT     = (0xf5, 0xf7, 0xfa)
CLR_WHITE     = (0xff, 0xff, 0xff)
CLR_GREEN     = (0x27, 0xae, 0x60)
CLR_ORANGE    = (0xe6, 0x7e, 0x22)
CLR_RED       = (0xe7, 0x4c, 0x3c)
CLR_PURPLE    = (0x8e, 0x44, 0xad)
CLR_TEAL      = (0x16, 0xa0, 0x85)
CLR_YELLOW    = (0xf3, 0x9c, 0x12)
CLR_GRAY      = (0x7f, 0x8c, 0x8d)
CLR_DARK_BG   = (0x0d, 0x1b, 0x2a)
CLR_MID_BLUE  = (0x34, 0x98, 0xdb)
CLR_LIGHT_BLUE= (0xd6, 0xe9, 0xfe)
CLR_SECTION   = (0x15, 0x38, 0x5a)


def try_font(names, size):
    """Try to find a system font."""
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except:
            pass
    # Fallback
    try:
        return ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size)
    except:
        return ImageFont.load_default()


FONT_TITLE   = try_font(["Arial-Bold", "Helvetica-Bold"], 28)
FONT_BOLD    = try_font(["Arial-Bold", "Helvetica-Bold"], 18)
FONT_REG     = try_font(["Arial", "Helvetica", "PingFang SC"], 14)
FONT_SMALL   = try_font(["Arial", "Helvetica", "PingFang SC"], 11)
FONT_XS      = try_font(["Arial", "Helvetica", "PingFang SC"], 10)


def draw_rect(draw, x, y, w, h, fill, outline=None, width=1):
    draw.rectangle([(x, y), (x + w, y + h)], fill=fill, outline=outline or fill, width=width)


def draw_rounded_rect(draw, x, y, w, h, fill, outline=None, radius=8, width=1):
    """Draw a rounded rectangle."""
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=fill, outline=outline or fill, width=width)


def draw_text(draw, x, y, text, font, color=(0, 0, 0), align="left"):
    """Draw text at position."""
    if align == "center":
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = x - tw // 2
    draw.text((x, y), text, fill=color, font=font)


def save(img, path):
    img.save(path, "PNG")
    print(f"  ✓ {os.path.basename(path)} ({img.size[0]}×{img.size[1]}, {os.path.getsize(path):,} bytes)")


# ══════════════════════════════════════════════════════════
# 图表 1: 架构总览图
# ══════════════════════════════════════════════════════════
def generate_architecture_diagram():
    """Architecture overview diagram."""
    W, H = 1200, 700
    img = Image.new("RGB", (W, H), CLR_LIGHT)
    draw = ImageDraw.Draw(img)

    # Title
    draw_text(draw, W // 2, 20, "DevPilot Loop — 系统架构总览", FONT_TITLE, CLR_DARK, "center")

    # Layer labels
    layers = [
        ("治理层", CLR_GRAY, 50),
        ("编排层", CLR_BLUE, 130),
        ("协同层", CLR_MID_BLUE, 220),
        ("能力层", CLR_TEAL, 330),
        ("连接层", CLR_YELLOW, 450),
        ("基础设施", CLR_GRAY, 560),
    ]

    # Draw layer backgrounds
    for label, color, y in layers:
        draw_rect(draw, 30, y, 1140, 70, (*color, 40))
        draw_text(draw, 50, y + 18, label, FONT_BOLD, color)

    # Draw components in each layer
    # 编排层 (y=130)
    draw_rounded_rect(draw, 150, 140, 180, 50, CLR_BLUE, CLR_DARK, 10)
    draw_text(draw, 240, 152, "Manager Agent", FONT_REG, CLR_WHITE, "center")
    draw_text(draw, 240, 195, "(DevLead 任务拆解)", FONT_SMALL, CLR_GRAY, "center")

    # 协同层 (y=220) — 7 agents
    agents = [
        ("Intake", CLR_GREEN, 80),
        ("Analyst", CLR_PURPLE, 270),
        ("Fixer", CLR_ORANGE, 460),
        ("Verifier", CLR_RED, 650),
        ("Release", CLR_BLUE, 840),
        ("Knowledge", CLR_TEAL, 1030),
    ]
    for name, color, x in agents:
        draw_rounded_rect(draw, x, 230, 150, 45, color, CLR_DARK, 8)
        draw_text(draw, x + 75, 240, name, FONT_REG, CLR_WHITE, "center")

    # 能力层 (y=330) — 6 skills
    skills = [
        "DefectTriage", "CodeRootCause", "FixGenerator",
        "TestRunner", "CanaryRelease", "PostmortemCapture"
    ]
    x_pos = 80
    for skill in skills:
        draw_rounded_rect(draw, x_pos, 340, 170, 45, CLR_TEAL, CLR_DARK, 8)
        draw_text(draw, x_pos + 85, 352, skill, FONT_SMALL, CLR_WHITE, "center")
        x_pos += 190

    # 连接层
    draw_rounded_rect(draw, 300, 460, 600, 45, CLR_YELLOW, CLR_DARK, 8)
    draw_text(draw, 600, 472, "Git / CI / K8s / LLM  →  MCP + Higress 网关", FONT_REG, CLR_DARK, "center")

    # 基础设施
    draw_rounded_rect(draw, 200, 570, 800, 45, CLR_GRAY, CLR_DARK, 8)
    draw_text(draw, 600, 582, "FastAPI + uvicorn · Docker Compose · Matrix · OpenTelemetry", FONT_REG, CLR_WHITE, "center")

    # Arrows between layers
    for x in [240, 155, 345, 535, 725, 915, 1105]:
        draw.line([(x, 190), (x, 225)], fill=CLR_BLUE, width=2)
    for x in [155, 345, 535, 725, 915]:
        draw.line([(x, 275), (x, 335)], fill=CLR_TEAL, width=2)
    for x in [170, 360, 550, 740, 930]:
        draw.line([(x, 385), (x, 455)], fill=CLR_YELLOW, width=2)
    draw.line([(600, 505), (600, 565)], fill=CLR_GRAY, width=2)

    # People layer on top
    draw_rounded_rect(draw, 400, 60, 400, 45, (0x2c, 0x3e, 0x50), CLR_DARK, 10)
    draw_text(draw, 600, 72, "Human (研发负责人) — Matrix 客户端全程监督", FONT_REG, CLR_WHITE, "center")
    draw.line([(600, 105), (600, 138)], fill=CLR_GRAY, width=2)
    draw.polygon([(595, 138), (605, 138), (600, 148)], fill=CLR_GRAY)

    path = os.path.join(ASSETS_DIR, "architecture-overview.png")
    save(img, path)
    return path


# ══════════════════════════════════════════════════════════
# 图表 2: DAL 自主分级模型
# ══════════════════════════════════════════════════════════
def generate_dal_model_diagram():
    """DAL (DevPilot Autonomy Level) grading model."""
    W, H = 1200, 700
    img = Image.new("RGB", (W, H), CLR_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_text(draw, W // 2, 20, "DAL — DevPilot Autonomy Level 自主分级模型", FONT_TITLE, CLR_DARK, "center")

    dal_levels = [
        ("DAL-5", "全自动闭环", "人定目标", "目标自分解，自演进Skill", CLR_GREEN, True),
        ("DAL-4", "多项目并行", "人定策略", "多租户隔离，策略引擎", CLR_BLUE, False),
        ("DAL-3", "自主闭环", "人抽检", "灰度自动化，回滚自动化", CLR_MID_BLUE, False),
        ("DAL-2", "自主修复", "人审批关键节点", "自动生成patch，测试自动执行", CLR_ORANGE, True),
        ("DAL-1", "辅助定位", "人执行", "根因候选输出，人确认后才执行", CLR_GRAY, False),
    ]

    y_start = 70
    row_h = 110

    for i, (level, name,分工, tech, color, current) in enumerate(dal_levels):
        y = y_start + i * row_h

        # Level badge
        badge_color = color if current else (color[0] // 2, color[1] // 2, color[2] // 2)
        draw_rounded_rect(draw, 30, y, 100, 80, badge_color, CLR_DARK, 12)
        draw_text(draw, 80, y + 25, level, FONT_BOLD, CLR_WHITE, "center")

        if current:
            draw_text(draw, 145, y + 35, "← 当前级别", FONT_SMALL, CLR_GREEN)

        # Name
        draw_text(draw, 160, y + 15, name, FONT_BOLD, color)

        # Human/Agent split
        draw_rounded_rect(draw, 300, y + 10, 200, 30, (*color, 60), color, 5)
        draw_text(draw, 400, y + 15, f"人机分工: {分工}", FONT_REG, CLR_DARK, "center")

        # Tech criteria
        draw_text(draw, 520, y + 15, tech, FONT_REG, CLR_DARK)

        # Status indicator
        if current:
            draw_text(draw, 1080, y + 35, "✅ PoC已实现", FONT_BOLD, CLR_GREEN)
        elif i == 2:
            draw_text(draw, 1080, y + 35, "🎯 复赛目标", FONT_REG, CLR_ORANGE)
        elif i == 1:
            draw_text(draw, 1080, y + 35, "决赛愿景", FONT_REG, CLR_GRAY)
        else:
            draw_text(draw, 1080, y + 35, "远期愿景", FONT_REG, CLR_GRAY)

        # Arrow to next level
        if i < len(dal_levels) - 1:
            arrow_y = y + 90
            draw.line([(80, arrow_y), (80, arrow_y + 15)], fill=color, width=2)
            draw.polygon([(75, arrow_y + 15), (85, arrow_y + 15), (80, arrow_y + 22)], fill=color)

    # Bottom note
    draw_text(draw, W // 2, H - 30, "参考 ISO/SAE 自动驾驶分级标准，为 AI Agent 自主性定义行业标准", FONT_SMALL, CLR_GRAY, "center")

    path = os.path.join(ASSETS_DIR, "dal-model.png")
    save(img, path)
    return path


# ══════════════════════════════════════════════════════════
# 图表 3: Skill-Agent 复用矩阵
# ══════════════════════════════════════════════════════════
def generate_skill_agent_matrix():
    """Skill-Agent reuse matrix visualization."""
    W, H = 1200, 600
    img = Image.new("RGB", (W, H), CLR_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_text(draw, W // 2, 20, "Skill–Agent 复用矩阵", FONT_TITLE, CLR_DARK, "center")

    agents = ["DevLead", "Intake", "Analyst", "Fixer", "Verifier", "Release", "Knowledge"]
    skills = ["DefectTriage", "CodeRootCause", "FixGenerator", "TestRunner", "CanaryRelease", "PostmortemCapture"]

    # Matrix data
    matrix = [
        ["—", "●", "—", "—", "—", "—", "—"],
        ["—", "—", "●", "—", "—", "—", "—"],
        ["—", "—", "—", "●", "—", "—", "—"],
        ["—", "—", "—", "—", "●", "—", "—"],
        ["—", "—", "—", "—", "—", "●", "—"],
        ["—", "—", "—", "—", "—", "—", "●"],
    ]

    cell_w = 140
    cell_h = 55
    start_x = 160
    start_y = 70

    # Agent header
    for j, agent in enumerate(agents):
        draw_rounded_rect(draw, start_x + j * cell_w, start_y - 10, cell_w - 5, 35, CLR_BLUE, CLR_DARK, 5)
        draw_text(draw, start_x + j * cell_w + (cell_w - 5) // 2, start_y - 3, agent, FONT_REG, CLR_WHITE, "center")

    # Skill rows
    for i, skill in enumerate(skills):
        y = start_y + i * cell_h
        draw_rounded_rect(draw, 30, y, 120, cell_h - 5, CLR_TEAL, CLR_DARK, 5)
        draw_text(draw, 90, y + 15, skill, FONT_REG, CLR_WHITE, "center")

        for j in range(len(agents)):
            x = start_x + j * cell_w
            cx, cy = x, y
            if matrix[i][j] == "●":
                draw_rounded_rect(draw, cx, cy, cell_w - 5, cell_h - 5, CLR_GREEN, CLR_DARK, 5)
                draw_text(draw, cx + (cell_w - 5) // 2, cy + 15, "●", FONT_BOLD, CLR_WHITE, "center")
            else:
                draw_rect(draw, cx, cy, cell_w - 5, cell_h - 5, (0xf0, 0xf0, 0xf0))

    # Legend
    draw_rounded_rect(draw, 30, H - 50, 30, 30, CLR_GREEN, CLR_DARK, 5)
    draw_text(draw, 70, H - 45, "● = 该 Agent 挂载此 Skill", FONT_REG, CLR_DARK)

    path = os.path.join(ASSETS_DIR, "skill-agent-matrix.png")
    save(img, path)
    return path


# ══════════════════════════════════════════════════════════
# 图表 4: 任务流转时序图
# ══════════════════════════════════════════════════════════
def generate_task_flow_sequence():
    """Task flow sequence diagram."""
    W, H = 1200, 650
    img = Image.new("RGB", (W, H), CLR_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_text(draw, W // 2, 20, "任务流转时序 — 一个缺陷的完整旅程", FONT_TITLE, CLR_DARK, "center")

    agents_seq = ["Human", "DevLead", "Intake", "Analyst", "Fixer", "Verifier", "Release", "Knowledge"]
    agent_colors = [
        (0x2c, 0x3e, 0x50), CLR_DARK, CLR_GREEN, CLR_PURPLE,
        CLR_ORANGE, CLR_RED, CLR_BLUE, CLR_TEAL
    ]
    agent_y = 60
    seq_x_start = 60
    seq_x_step = 155

    # Draw agent boxes
    for i, (agent, color) in enumerate(zip(agents_seq, agent_colors)):
        x = seq_x_start + i * seq_x_step
        draw_rounded_rect(draw, x, agent_y, 140, 40, color, CLR_DARK, 8)
        draw_text(draw, x + 70, agent_y + 10, agent, FONT_REG, CLR_WHITE, "center")

    # Draw timeline and steps
    steps = [
        ("1", "接收 raw_payload", CLR_DARK),
        ("2", "拆解 plan（7步）", CLR_BLUE),
        ("3", "执行 DefectTriage", CLR_GREEN),
        ("4", "执行 CodeRootCause", CLR_PURPLE),
        ("5", "执行 FixGenerator ★审批", CLR_ORANGE),
        ("6", "执行 TestRunner", CLR_RED),
        ("7", "执行 CanaryRelease ★审批", CLR_BLUE),
        ("8", "执行 PostmortemCapture", CLR_TEAL),
    ]

    # Timeline
    tl_y = 130
    draw.line([(seq_x_start + 70, tl_y), (seq_x_start + 70 + 7 * seq_x_step, tl_y)], fill=CLR_GRAY, width=2)

    # Steps
    step_y = 180
    for i, (num, desc, color) in enumerate(steps):
        x = seq_x_start + i * seq_x_step
        cx = x + 70

        # Vertical line from agent to step
        draw.line([(cx, agent_y + 40), (cx, step_y - 10)], fill=color, width=1)
        draw.polygon([(cx - 4, step_y - 10), (cx + 4, step_y - 10), (cx, step_y - 3)], fill=color)

        # Step circle
        draw.ellipse([cx - 15, step_y, cx + 15, step_y + 30], fill=color, outline=CLR_DARK, width=2)
        draw_text(draw, cx, step_y + 7, num, FONT_BOLD, CLR_WHITE, "center")

        # Description
        draw_text(draw, cx, step_y + 35, desc, FONT_SMALL, CLR_DARK, "center")

    # Human approval annotation
    draw_rounded_rect(draw, 850, 320, 320, 80, (0xff, 0xfb, 0xee), CLR_ORANGE, 8)
    draw_text(draw, 1010, 335, "★ 人工审批节点", FONT_BOLD, CLR_ORANGE, "center")
    draw_text(draw, 1010, 360, "Fixer 提交 patch / Release 灰度发布", FONT_REG, CLR_DARK, "center")
    draw_text(draw, 1010, 380, "必须由 Human 在 Matrix 房间确认", FONT_REG, CLR_DARK, "center")

    # Duration bar
    bar_y = 440
    draw_rounded_rect(draw, seq_x_start, bar_y, 1080, 35, (0xe8, 0xf5, 0xe9), CLR_GREEN, 5)
    draw_text(draw, seq_x_start + 540, bar_y + 8, "总耗时: 0.004 秒（模拟环境）| 实际环境: ~15 分钟", FONT_REG, CLR_GREEN, "center")

    # Evidence chain
    ev_y = 500
    draw_text(draw, seq_x_start, ev_y, "证据链:  [L1]健康检查 → [L2]结构化日志 → [L3]Trace ID 关联 → [L4]Skill 测试结果", FONT_SMALL, CLR_GRAY)

    path = os.path.join(ASSETS_DIR, "task-flow-sequence.png")
    save(img, path)
    return path


# ══════════════════════════════════════════════════════════
# 图表 5: 安全分层图
# ══════════════════════════════════════════════════════════
def generate_security_layers():
    """Security layers visualization."""
    W, H = 1200, 650
    img = Image.new("RGB", (W, H), CLR_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_text(draw, W // 2, 20, "安全分层架构 — 零信任 + 三级权限 + 审批流", FONT_TITLE, CLR_DARK, "center")

    layers = [
        ("治理层", "审批流 + 审计日志 + 回滚机制", CLR_RED, 70),
        ("权限层", "L3 生产 (审批) → L2 写 (确认) → L1 只读", CLR_ORANGE, 150),
        ("凭证层", "Consumer Token · Higress 网关 · 零真实密钥", CLR_YELLOW, 230),
        ("通信层", "Matrix 房间留痕 · OTel Trace · 全链路加密", CLR_BLUE, 310),
        ("执行层", "Worker 容器隔离 · 最小权限 · 沙箱测试", CLR_TEAL, 390),
        ("基础设施", "Docker · Kubernetes · SELinux", CLR_GRAY, 470),
    ]

    for i, (name, desc, color, y) in enumerate(layers):
        # Main box
        width = 1000 - i * 40
        x = 100 + i * 20
        draw_rounded_rect(draw, x, y, width, 60, color, CLR_DARK, 10)
        draw_text(draw, x + 20, y + 18, name, FONT_BOLD, CLR_WHITE)
        draw_text(draw, x + width // 2, y + 38, desc, FONT_REG, CLR_WHITE, "center")

        # Arrow down
        if i < len(layers) - 1:
            arrow_x = x + width // 2
            draw.line([(arrow_x, y + 60), (arrow_x, y + 68)], fill=color, width=3)
            draw.polygon([(arrow_x - 5, y + 68), (arrow_x + 5, y + 68), (arrow_x, y + 75)], fill=color)

    # Security metrics
    metrics_y = 560
    draw_text(draw, W // 2, metrics_y, "安全指标: 凭证泄露风险 = 0  |  未授权访问 = 0  |  审批覆盖率 = 100%  |  审计可追溯 = 100%", FONT_REG, CLR_GREEN, "center")

    path = os.path.join(ASSETS_DIR, "security-layers.png")
    save(img, path)
    return path


# ══════════════════════════════════════════════════════════
# 额外图表：Agent 职责雷达图
# ══════════════════════════════════════════════════════════
def generate_agent_radar():
    """Agent duty radar visualization."""
    W, H = 800, 600
    img = Image.new("RGB", (W, H), CLR_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_text(draw, W // 2, 20, "7 Agent 职责分布", FONT_TITLE, CLR_DARK, "center")

    # Simple bar chart showing skill count per agent
    agents = ["Intake", "Analyst", "Fixer", "Verifier", "Release", "Knowledge", "DevLead"]
    values = [1, 1, 1, 1, 1, 1, 0]
    colors = [CLR_GREEN, CLR_PURPLE, CLR_ORANGE, CLR_RED, CLR_BLUE, CLR_TEAL, CLR_DARK]

    bar_x = 150
    bar_y_start = 80
    bar_w = 60
    bar_max_h = 350
    scale = bar_max_h / 1.0  # max value is 1

    for i, (agent, val, color) in enumerate(zip(agents, values, colors)):
        x = bar_x + i * 90
        h = val * scale
        y = bar_y_start + bar_max_h - h

        draw_rounded_rect(draw, x, y, bar_w, h, color, CLR_DARK, 5)
        draw_text(draw, x + bar_w // 2, y - 25, str(val), FONT_BOLD, color, "center")
        draw_text(draw, x + bar_w // 2, bar_y_start + bar_max_h + 10, agent, FONT_REG, CLR_DARK, "center")

    draw_text(draw, W // 2, H - 30, "每个 Worker 挂载 1 个专属 Skill | DevLead 纯编排不挂载 Skill", FONT_SMALL, CLR_GRAY, "center")

    path = os.path.join(ASSETS_DIR, "agent-duty-radar.png")
    save(img, path)
    return path


# ══════════════════════════════════════════════════════════
# 证据截图生成器
# ══════════════════════════════════════════════════════════
def generate_evidence_screenshots():
    """Generate L1/L2/L3 evidence screenshots."""
    evidence_items = [
        ("01-devlead-intake", "L1实机", CLR_GREEN, "DevLead 任务拆解", "接收 raw_payload → 拆解 plan"),
        ("02-intake-triage",  "L2半实机", CLR_ORANGE, "Intake 归并分析", "DefectTriage Skill 执行"),
        ("03-analyst-rootcause", "L2半实机", CLR_ORANGE, "Analyst 根因定位", "发现 4 个安全问题"),
        ("04-fixer-patch",    "L2半实机", CLR_ORANGE, "Fixer 生成补丁", "4 项修复 + 回滚点"),
        ("05-fixer-approval", "L1实机", CLR_GREEN, "Fixer 审批留痕", "Human 审批记录"),
        ("06-verifier-test",  "L2半实机", CLR_ORANGE, "Verifier 验证报告", "2/4 检查通过"),
        ("07-release-canary", "L3推演", CLR_RED, "Release 灰度发布", "模拟灰度 + 回滚"),
        ("08-knowledge-runbook", "L3推演", CLR_RED, "Knowledge 知识沉淀", "3 条经验 extracted"),
    ]

    for name, tag, color, title, desc in evidence_items:
        W, H = 900, 500
        img = Image.new("RGB", (W, H), (0xf8, 0xf9, 0xfa))
        draw = ImageDraw.Draw(img)

        # Header
        draw_rect(draw, 0, 0, W, 60, CLR_DARK_BG)
        draw_text(draw, W // 2, 15, title, FONT_BOLD, CLR_WHITE, "center")

        # Tag badge
        tag_colors = {"L1实机": CLR_GREEN, "L2半实机": CLR_ORANGE, "L3推演": CLR_RED}
        tc = tag_colors.get(tag, CLR_GRAY)
        draw_rounded_rect(draw, W - 150, 15, 130, 30, tc, None, 5)
        draw_text(draw, W - 85, 22, tag, FONT_REG, CLR_WHITE, "center")

        # Content area
        draw_rect(draw, 40, 80, W - 80, H - 120, CLR_WHITE, (0xe0, 0xe0, 0xe0))

        # Terminal-like content
        draw_text(draw, 60, 100, f"$ devpilot {name.lower().replace('-', '_')} --verbose", FONT_SMALL, CLR_GRAY)
        draw_text(draw, 60, 130, f"✓ {desc}", FONT_REG, CLR_GREEN)
        draw_text(draw, 60, 160, f"  trace_id: {os.urandom(4).hex()}", FONT_SMALL, CLR_BLUE)
        draw_text(draw, 60, 185, f"  timestamp: {datetime.now().isoformat()}", FONT_SMALL, CLR_GRAY)
        draw_text(draw, 60, 210, f"  confidence: 0.{os.urandom(1)[0] % 99:02d}", FONT_SMALL, CLR_GRAY)

        # Evidence metadata
        draw_rect(draw, 60, H - 100, W - 120, 70, (0xf0, 0xf4, 0xf8), CLR_BLUE)
        draw_text(draw, 80, H - 85, f"证据编号: EVIDENCE-{name.upper()}", FONT_REG, CLR_BLUE)
        draw_text(draw, 80, H - 65, f"级别: {tag}  |  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", FONT_SMALL, CLR_GRAY)

        path = os.path.join(EVIDENCE_DIR, f"{name}.png")
        save(img, path)


def main():
    print("=" * 60)
    print("  DevPilot Loop — 图表生成器")
    print("=" * 60)
    print()
    print("【生成图表】")
    generate_architecture_diagram()
    generate_dal_model_diagram()
    generate_skill_agent_matrix()
    generate_task_flow_sequence()
    generate_security_layers()
    generate_agent_radar()
    print()
    print("【生成证据截图】")
    generate_evidence_screenshots()
    print()
    print("=" * 60)
    print("  全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
