from typing import List, Dict
from pydantic import BaseModel, Field


# Analyst
class CadrageReport(BaseModel):
    needs: List[str]
    constraints: List[str]
    actors: List[str]
    risks: List[str]
    clarification_questions: List[str]


# Architect
class ADR(BaseModel):
    title: str
    context: str
    decision: str
    consequences: list


# Software Engineer
class SOLIDCode(BaseModel):
    class_name: str
    methods: Dict[str, str]
    unit_tests: Dict[str, str]


# PM Analyst
class TechnicalSpec(BaseModel):
    """
    Domain model representing a single technical requirement.
    This is a core business object used across all agents.
    """
    title: str = Field(description="Short title of the requirement")
    description: str = Field(description="Detailed technical explanation")
    priority: str = Field(description="Priority level (Must, Should, Could, Won't)")