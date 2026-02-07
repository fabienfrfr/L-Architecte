# ADR 003: Selection of NiceGUI

**Status:** Accepted

**Decider:** Fabien Furfaro ( **TheArchitect** )

## 1. Problem

Traditional **React/FastAPI** stacks create "stack friction" for solo developers: duplicated models (Pydantic/TypeScript), complex API serialization, and high maintenance overhead.

## 2. Comparison

* **Streamlit** : ❌ Rejected. Script reruns on every interaction; too slow and rigid for complex agentic states.
* **Reflex** : ❌ Rejected. Steep learning curve (Web-centric); over-engineered for local LLM tools.
* **NiceGUI** : ✅  **Chosen** . Full-stack Python, real-time reactivity without reruns, and native `asyncio` support for LangGraph/Ollama.

## 3. Decision Drivers

1. **Unified Stack** : Single language (Python) and single model source (Pydantic).
2. **No Internal API** : UI and Logic share the same process; no need for `GET`/`POST` for local data flow.
3. **Real-time Streaming** : Native `async` support to stream agent thoughts directly from Ollama to the UI.

## 4. Consequences

* **Pros** : 10x faster development, simplified Docker deployment, unified debugging.
* **Cons** : Requires specific Linux process handling to avoid multiprocessing conflicts on Ubuntu.
