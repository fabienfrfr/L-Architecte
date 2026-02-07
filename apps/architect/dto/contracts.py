from pydantic import BaseModel, Field
from typing import List

class ArchitectureRequest(BaseModel):
    requirements: str


class PMAnalysisReport(BaseModel):
    """
    Contract representing the initial SMART analysis of requirements.
    Now with default values for maximum robustness.
    """
    is_smart: bool = Field(default=False, description="True if requirements meet SMART criteria")
    gaps: List[str] = Field(default_factory=list, description="List of missing information")
    hypotheses: List[str] = Field(default_factory=list, description="Technical assumptions")
    content: str = ""