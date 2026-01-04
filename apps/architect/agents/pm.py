from langchain_core.prompts import ChatPromptTemplate
from apps.architect.core.llm import get_llm


class PMAgent:
    def __init__(self):
        self.llm = get_llm(json_mode=True)
        self.prompt = ChatPromptTemplate.from_messages(
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

    def check_requirements(self, requirements: str):
        chain = self.prompt | self.llm
        return chain.invoke({"requirements": requirements})
