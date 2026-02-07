from typing import Dict
from apps.architect.domain.models import ADR


class ArchitectAgent:
    def generate_c4_diagram(self, requirements: Dict) -> str:
        return """graph TD
            A[Client] --> B[FastAPI]
            B --> C[Architect Agent]"""

    def generate_adr(self, context: Dict) -> ADR:
        return ADR(
            title="Use ChromaDB",
            context="Need local RAG",
            decision="Deploy ChromaDB in Docker",
            consequences=["Pros: Local", "Cons: No HA"],
        )


ARCHITECT_CORE_RULES = """
CORE ARCHITECTURAL RULES:
1. **Less is More**: Always favor the simplest solution that meets the requirements. 
2. **Minimize Assumptions**: Do not build for "future" use cases that are not explicitly requested (YAGNI - You Ain't Gonna Need It).
3. **Check Existing Standards**: Before proposing a custom solution, verify if a Python Standard Library module or a widely-adopted industry standard (e.g., Pydantic, SQLAlchemy) already solves the problem.
4. **Occam's Razor**: If two designs provide the same result, the one with fewer moving parts and fewer dependencies is the correct one.
"""
