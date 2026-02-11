from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class AgentStateDTO(BaseModel):
    requirements: str
    charter_data: Dict[str, Any] = Field(default_factory=dict)
    analysis_report: Optional[Dict[str, Any]] = None
    architecture_specs: Optional[Dict[str, Any]] = None
    final_code: Optional[Dict[str, Any]] = None
    is_ready: bool = False
    retry_count: int = 0
