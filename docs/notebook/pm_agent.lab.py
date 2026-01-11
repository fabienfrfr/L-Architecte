# %% [markdown]
# # 🏗️ TheArchitect: Minimalist R&D Lab
# **Author:** Fabien Furfaro
# **Project:** [AgenticArchitect](https://github.com/fabienfrfr/AgenticArchitect)
# 
# > **Methodology:** Functional Testing (Playground Mode)
# > **Goal:** Testing multi-step agent logic: Analysis -> Generation.

# %%
import asyncio
import json
import nest_asyncio
from apps.architect.core.llm import get_llm

nest_asyncio.apply()

# %% [markdown]
# ## 1. Functional Playground (Multi-Capability)

# %%
async def run_pm_analysis(user_input: str):
    """Capability 1: Check SMART criteria and identify gaps."""
    print(f"⏳ [Step 1] Analyzing Requirements...")
    llm = get_llm(json_mode=True)
    
    system_prompt = (
        "Role: Strict Project Manager.\n"
        "Analyze if input is SMART. If not, set is_smart: false and list gaps.\n"
        "Return ONLY JSON: {\"is_smart\": bool, \"gaps\": [], \"project_name\": \"...\"}"
    )
    
    try:
        response = await llm.ainvoke(f"{system_prompt}\n\nInput: {user_input}")
        content = response.content if hasattr(response, 'content') else str(response)
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

async def generate_hypotheses_specs(analysis_result: dict):
    """Capability 2: Take the gaps and propose technical solutions."""
    print(f"⏳ [Step 2] Filling Gaps with Hypotheses...")
    llm = get_llm(json_mode=True)
    
    system_prompt = (
        "Role: Technical Architect.\n"
        "Based on the identified gaps, propose 3 technical hypotheses to unblock the project.\n"
        "Return ONLY JSON: {\"hypotheses\": [\"tech stack assumption\", ...]}"
    )
    
    try:
        response = await llm.ainvoke(f"{system_prompt}\n\nAnalysis: {json.dumps(analysis_result)}")
        content = response.content if hasattr(response, 'content') else str(response)
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

# %% [markdown]
# ## 2. Procedural Execution (The Workflow)

# %%
query = "I want a library management API in Python"
print(f"🚀 Starting Playground Pipeline: '{query}'")

# Step 1: Analysis
analysis = await run_pm_analysis(query)

if not analysis.get("is_smart"):
    print(f"❌ Project is not SMART. Gaps: {analysis.get('gaps')}")
    
    # Step 2: Adaptive Logic (Filling Gaps)
    improvements = await generate_hypotheses_specs(analysis)
    
    print("\n[TheArchitect Adaptive Response]")
    for h in improvements.get('hypotheses', []):
        print(f" 💡 Hypothesis: {h}")
else:
    print("✅ Project is SMART and ready for Analyst stage.")

# %% [markdown]
# ## 3. Comparison with Source (Parity Check)

# %%
from apps.architect.agents.pm import PMAgent 

def test_real_agent():
    """
    Validates the official project logic.
    TODO: Refactor PMAgent to include multi-method support (check_requirements + generate_hypotheses)
    based on the playground tests above. --> add in orchestrator this cycle also.
    """
    print("\n" + "-"*10 + " Official Source Test " + "-"*10)
    agent = PMAgent()
    
    # Current single-method implementation
    result = agent.check_requirements("I want a library management API in Python")
    
    print("\n--- Official Agent Output ---")
    if hasattr(result, 'content'):
        print(result.content)
    else:
        print(json.dumps(result, indent=2))

test_real_agent()