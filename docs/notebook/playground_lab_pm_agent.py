# %% [markdown]
# # 🏗️ TheArchitect: Agentic R&D Lab
# **Author:** Fabien Furfaro
# **Project:** [AgenticArchitect](https://github.com/fabienfrfr/AgenticArchitect)
#
# > **Official R&D Sandbox** | *Methodology: Analyst -> Architect -> Engineer*
#
# This lab allows for isolated testing of the **TheArchitect** core logic.
# It simulates the first two stages of the agentic pipeline using **Gemma 3 270m**.

# %% [markdown]
# ## 1. Environment & Requirements
# Run this cell to initialize the persistent session and load the model.

# %%
import asyncio
import json
import nest_asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

nest_asyncio.apply()

# Configuration
LLM_MODEL = "gemma3:270m"
OLLAMA_URL = "http://localhost:11434"

# Persistent LLM Connection
llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_URL, format="json")
print(f"🚀 System Online | Model: {LLM_MODEL} | GitHub: fabienfrfr/AgenticArchitect")

# %% [markdown]
# ## 2. Methodology: Structured Project Charter
# Definition of the strict data contract for the PM Agent.


# %%
class CadrageReport(BaseModel):
    project_name: str = Field(description="Formal name of the project")
    vision: str = Field(description="High-level project goals")
    needs: List[str] = Field(description="List of functional requirements")
    constraints: List[str] = Field(
        description="Technical boundaries (Python, Docker, SQL)"
    )
    is_smart: bool = Field(description="Validation: Is the request actionable?")
    missing_info: Optional[str] = Field(description="Feedback if is_smart is False")


parser = JsonOutputParser(pydantic_object=CadrageReport)
print("✅ Data Contract defined.")

# %% [markdown]
# ## 3. Agentic Nodes
# ### A. The PM Agent (The Gatekeeper)
# Transforms raw user intent into a validated JSON charter.

# %%
PM_PROMPT = """
Role: Lead Project Manager (TheArchitect)
Task: Produce a JSON CadrageReport.
Requirement: Be strict on SMART criteria.

{format_instructions}

User Input: {input}
"""


async def run_pm(user_input: str):
    prompt = ChatPromptTemplate.from_template(PM_PROMPT)
    chain = prompt | llm | parser
    return await chain.ainvoke(
        {"input": user_input, "format_instructions": parser.get_format_instructions()}
    )


# %% [markdown]
# ### B. The Analyst Agent (BDD Expert)
# Converts the validated charter into Gherkin features.

# %%
ANALYST_PROMPT = """
Role: System Analyst
Context: {charter}
Task: Generate Gherkin (.feature) files.
Output: Markdown blocks only.
"""


async def run_analyst(charter: dict):
    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT)
    chain = prompt | llm
    return await chain.ainvoke({"charter": json.dumps(charter)})


# %% [markdown]
# ## 4. Execution Pipeline
# Modify the `query` below and run this cell to test the full flow.


# %%
async def execute_playground():
    # Change this query to test different scenarios
    query = "I want a Python API for library management with Docker and SQL"

    # Step 1: PM Processing
    charter = await run_pm(query)
    print(f"\nPM Status: {'✅ SMART' if charter['is_smart'] else '❌ INCOMPLETE'}")

    # Step 2: Analyst Processing
    if charter["is_smart"]:
        specs = await run_analyst(charter)
        print("\n--- BDD SPECIFICATIONS ---\n")
        print(specs)
    else:
        print(f"Gaps identified: {charter['missing_info']}")


# Direct execution in the Jupyter/Interactive kernel
await execute_playground()
