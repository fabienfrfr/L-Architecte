from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from apps.architect.dao.llm_client import get_llm
from apps.architect.dto.contracts import PMAnalysisReport
from apps.architect.domain.models import TechnicalSpec

class PMAgent:
    """
    Project Manager Agent responsible for requirements validation and specification.
    Follows SRP (Single Responsibility Principle) by delegating data structures 
    to Contracts and Domain models.
    """

    def __init__(self):
        # DAO Layer: Fetching the LLM client with JSON enforcement
        self.llm = get_llm(json_mode=True)
        
        self.structured_llm = self.llm.with_structured_output(PMAnalysisReport)
        
        # PROMPTS: Centralized prompt management for the agent's 'brain'
        self.check_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a strict Project Manager. Analyze the client requirements using SMART criteria. "
                "If ANY detail is missing (data sources, deadliness, specific tech stack, scale), "
                "set 'is_smart' to false. "
                "Return ONLY JSON with keys: 'is_smart' (bool), 'gaps' (list), 'hypotheses' (list)."
            ),
            ("user", "{requirements}"),
        ])
        
        self.gen_prompt = ChatPromptTemplate.from_template(
            "Based on these validated points, generate 5 detailed technical requirements. "
            "Return a list of JSON objects with keys: 'title', 'description', 'priority'. "
            "Points: {points}"
        )

    def check_requirements(self, requirements: str) -> PMAnalysisReport:
        """
        Validates raw input against SMART criteria.
        Robust implementation using safe dictionary access instead of try/except.
        """
        chain = self.check_prompt | self.structured_llm
        
        report = chain.invoke({"requirements": requirements})
        
        report.content = requirements
        return report

    def generate_specs(self, validated_data: Dict[str, Any]) -> List[TechnicalSpec]:
        """
        Generates formal technical specifications from validated data.
        Returns a list of Domain-level TechnicalSpec objects.
        """
        chain = self.gen_prompt | self.llm | JsonOutputParser()
        raw_list = chain.invoke({"points": validated_data})
        
        # Logic: Domain Mapping - transform raw list to Domain Models
        # Supports both direct list response or nested list in dict
        if isinstance(raw_list, dict) and "requirements" in raw_list:
            raw_list = raw_list["requirements"]
            
        return [TechnicalSpec(**item) for item in raw_list]

    def fill_gaps_with_hypotheses(self, report: PMAnalysisReport) -> List[str]:
        """
        Specialized logic to handle missing info by generating technical assumptions.
        Uses the PMAnalysisReport contract as input.
        """
        prompt = ChatPromptTemplate.from_template(
            "Generate technical hypotheses for these gaps: {gaps}. "
            "Return JSON with a 'hypotheses' list."
        )
        chain = prompt | self.llm | JsonOutputParser()
        
        response = chain.invoke({"gaps": report.gaps})
        return response.get("hypotheses", [])