# %% [markdown]
# # 🏗️ TheArchitect Lab
# AgenticArchitect - Fabien Furfaro

# %%
# BLOC 1 : SETUP (À lancer une seule fois)
import asyncio
import nest_asyncio
from pydantic import BaseModel
from langchain_community.llms import Ollama

nest_asyncio.apply()
llm = Ollama(model="gemma3:270m", base_url="http://localhost:11434")


class CadrageReport(BaseModel):
    project_name: str
    is_smart: bool


print("✅ Setup terminé. Gemma 3 est prêt.")


# %%
# BLOC 2 : TEST (À lancer autant que tu veux)
async def test():
    # Ici tu peux modifier ta query sans tout relancer
    query = "Create a library system"
    print(f"Testing: {query}")
    # Ton code d'agent ici...


asyncio.run(test())
