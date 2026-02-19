### # ADR 006: Transition to PydanticAI

**Status:** Accepted

**Decider:** Fabien Furfaro

**Context:** The project requires a more robust, type-safe, and production-ready framework than LangGraph. We need seamless integration with observability and orchestration tools without adding heavy boilerplate.

**Decision:** We will use **PydanticAI**. It provides a professional-grade agent framework that natively integrates with **Logfire** (for observability) and **Prefect** (for orchestration), ensuring a unified and typed developer experience.

**Consequences:**

* **Pros:**
* **Type-Safe Development:** Leveraging Pydantic for strict input/output validation.
* **Built-in Observability:** Native integration with Logfire for deep debugging.
* **Native Orchestration:** Direct support for Prefect to manage complex task lifecycles.
* **Minimalist Logic:** Replaces complex state machines with standard Python control flow.


* **Cons:**
* **Framework Lock-in:** Strong dependency on the Pydantic ecosystem.

**Source:** [PydanticAI Docs](https://ai.pydantic.dev/)