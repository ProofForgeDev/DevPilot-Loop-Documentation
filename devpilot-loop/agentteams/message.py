"""MessageBus — Agent 间消息通信"""
import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("devpilot.messages")

class MessageBus:
    """AgentTeams 兼容的消息总线"""
    
    def __init__(self, room: str = "#default:devpilot.local"):
        self.room = room
        self._messages: List[Dict[str, Any]] = []
        self._trace_id = str(uuid.uuid4())[:16]
    
    def publish(self, sender: str, message: Dict[str, Any]) -> str:
        msg_id = str(uuid.uuid4())[:12]
        entry = {
            "id": msg_id,
            "sender": sender,
            "room": self.room,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": self._trace_id,
        }
        self._messages.append(entry)
        logger.debug(f"Message published: {msg_id} from {sender} to {self.room}")
        return msg_id
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        return self._messages[-limit:]
    
    def get_trace_id(self) -> str:
        return self._trace_id
