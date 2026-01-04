`{cmd=true}`

Playgrounds notebook to construct PMAgent

### 1. Requirements & Setup

```python
# Cell 1: Setup and imports
import asyncio
import json
from typing import TypedDict, List, Optional
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate

# Mirroring  apps/architect/core/state.py
class AgenticState(TypedDict):
    requirements: str
    project_charter: Optional[str]  # The "CadrageReport"
    analysis: Optional[str]         # BDD Features
    architecture: Optional[str]     # C4 Diagrams
    code: Optional[str]             # SOLID Code
    errors: List[str]

# Initialize Gemma 3 via Ollama
llm = Ollama(model="gemma3:270m", base_url="http://localhost:11434")

```

### 2. The PM Agent (Generating the Charter)

This follows the logic found in `pm.feature`: "When the analyst agent processes it, then it should return a CadrageReport".

```python
# Cell 2: PM Agent Logic
PM_PROMPT_TEMPLATE = """
Role: Lead Project Manager (TheArchitect)
Context: You are the first agent in a "Analyst -> Architect -> Engineer" workflow.

Task: Transform the User Input into a formal "CadrageReport".
This report MUST be structured in Markdown and include:
1. PROJECT OVERVIEW: Clear vision.
2. CORE FEATURES: Minimum 3 functional requirements.
3. TECHNICAL CONSTRAINTS: Based on Python/Docker (as per project structure).
4. SMART VALIDATION: Is the request feasible and complete?

User Input: {input}

Return only the Markdown Project Charter.
"""

async def pm_node_test(state: AgenticState) -> AgenticState:
    print("--- PM STARTING: Generating Project Charter ---")
    prompt = PM_PROMPT_TEMPLATE.format(input=state["requirements"])
    
    response = llm.invoke(prompt)
    
    state["project_charter"] = response
    return state

```

### 3. Testing the Chain (PM -> Analyst)

This ensures that the output of the PM is actually useful for the next agent.

```python
# Cell 3: Analyst Logic (Consuming the PM output)
ANALYST_PROMPT_TEMPLATE = """
Role: System Analyst
Task: Create BDD Scenarios (Gherkin) based ONLY on the following Project Charter.

Project Charter:
{charter}

Output: 1 or 2 .feature files (Gherkin format).
"""

async def analyst_node_test(state: AgenticState) -> AgenticState:
    print("--- ANALYST STARTING: Generating BDD Specs ---")
    # Crucial: The Analyst looks at the Charter, NOT the raw requirements
    prompt = ANALYST_PROMPT_TEMPLATE.format(charter=state["project_charter"])
    
    response = llm.invoke(prompt)
    state["analysis"] = response
    return state

```

### 4. Running the Test

```python
# Cell 4: Execution
async def main_test():
    # Initial input
    initial_state: AgenticState = {
        "requirements": "I want a Python API for library management with Docker and SQL",
        "project_charter": None,
        "analysis": None,
        "architecture": None,
        "code": None,
        "errors": []
    }
    
    # 1. PM Step
    state_after_pm = await pm_node_test(initial_state)
    print("\n[PM OUTPUT - PROJECT CHARTER]:")
    print(state_after_pm["project_charter"])
    
    # 2. Analyst Step
    state_after_analyst = await analyst_node_test(state_after_pm)
    print("\n[ANALYST OUTPUT - BDD SPECS]:")
    print(state_after_analyst["analysis"])

# Run the notebook test
await main_test()

```