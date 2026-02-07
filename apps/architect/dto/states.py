from pydantic import BaseModel, Field
from typing import Dict, Any


class AgentStateDTO(BaseModel):
    requirements: str
    charter_data: Dict[str, Any] = Field(default_factory=dict)
    is_ready: bool = False
    retry_count: int = 0
