from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

class CadrageReport(BaseModel):
    needs: List[str]
    constraints: List[str]
    actors: List[str]
    risks: List[str]
    clarification_questions: List[str]

class IAnalystAgent(ABC):
    @abstractmethod
    def analyze(self, cdc_text: str) -> CadrageReport:
        pass

class AnalystAgent(IAnalystAgent):
    def analyze(self, cdc_text: str) -> CadrageReport:
        return CadrageReport(
            needs=["Automate data validation"],
            constraints=["Budget: $50K"],
            actors=["Data Team"],
            risks=["High risk of scope creep"],
            clarification_questions=["What are the KPIs?"]
        )
