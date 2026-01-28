from langchain_core.prompts import ChatPromptTemplate
from apps.architect.core.llm import get_llm


class PMAgent:
    def __init__(self):
        self.llm = get_llm(json_mode=True)
        self.check_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a strict Project Manager. Analyze the client requirements using SMART criteria. "
                    "If ANY detail is missing (data sources, deadliness, specific tech stack, scale), "
                    "set 'is_smart' to false. "
                    "Return ONLY JSON with keys: 'is_smart' (bool), 'gaps' (list), 'hypotheses' (list)."
                    "HYPOTHESES: Generate realistic technical assumptions to fill the gaps. ",
                ),
                ("user", "{requirements}"),
            ]
        )
        self.gen_prompt = ChatPromptTemplate.from_template(
            "Based on these validated points, generate 5 detailed technical requirements: {points}"
        )

    def check_requirements(self, requirements: str):
        chain = self.check_prompt | self.llm
        return chain.invoke({"requirements": requirements})

    def generate_specs(self, validated_data: dict):
        chain = self.gen_prompt | self.llm
        return chain.invoke({"points": validated_data})

    def fill_gaps_with_hypotheses(self, report: dict):
        prompt = ChatPromptTemplate.from_template(
            "Generate hypotheses for these gaps: {gaps}"
        )
        chain = prompt | self.llm
        return chain.invoke({"gaps": report.get("gaps", [])})
