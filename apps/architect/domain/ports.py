from abc import ABC, abstractmethod
from apps.architect.domain.models import CadrageReport

class IAnalystAgent(ABC):
    """
    Domain Port (Interface).
    Defines the contract for requirements analysis.
    """
    @abstractmethod
    async def analyze(self, cdc_text: str) -> CadrageReport:
        """Analyzes a CDC and returns a validated CadrageReport."""
        pass