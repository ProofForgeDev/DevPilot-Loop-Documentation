"""SkillRegistry — Skill 注册中心"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("devpilot.registry")

class SkillRegistry:
    """Skill 注册与管理"""
    
    def __init__(self):
        self._skills: Dict[str, dict] = {}
    
    def register(self, name: str, skill_class, version: str = "1.0.0"):
        self._skills[name] = {
            "name": name,
            "class": skill_class,
            "version": version,
            "registered_at": str(__import__('datetime').datetime.now(__import__('datetime').timezone.utc)),
        }
        logger.info(f"Registered skill: {name}@{version}")
    
    def get(self, name: str) -> Optional[dict]:
        return self._skills.get(name)
    
    def list_all(self) -> List[dict]:
        return [{"name": s["name"], "version": s["version"]} for s in self._skills.values()]
    
    def __len__(self):
        return len(self._skills)
