"""DevPilot Loop Skills Package — 6 个可安装 Skill 模块"""

from .base import BaseSkill
from .code_review.skill import CodeReviewSkill
from .test_generation.skill import TestGenerationSkill
from .doc_writing.skill import DocWritingSkill
from .security_scan.skill import SecurityScanSkill
from .perf_analysis.skill import PerfAnalysisSkill
from .deploy_verification.skill import DeployVerificationSkill

__all__ = [
    "BaseSkill",
    "CodeReviewSkill",
    "TestGenerationSkill",
    "DocWritingSkill",
    "SecurityScanSkill",
    "PerfAnalysisSkill",
    "DeployVerificationSkill",
]
__version__ = "2.0.0"
