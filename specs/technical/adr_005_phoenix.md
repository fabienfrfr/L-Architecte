# ADR 005: Integration of Arize Phoenix for Agentic Observability

**Status:** Accepted (Supersedes Langfuse)

**Context:** The **AgenticArchitect** system (LangGraph + Ollama/Gemma) requires deep observability to trace agent reasoning and "Chain of Thought." Initial evaluation of Langfuse revealed excessive infrastructure overhead (PostgreSQL + ClickHouse) for local development on limited hardware.

**Decision:** We will use **Arize Phoenix** as the primary observability layer. Integration will be handled via **OpenTelemetry (OTLP)** standards to ensure a lightweight, vendor-neutral footprint.

**Consequences:**
* **Pros:** * **Resource Efficient:** Single Docker container; ~70% less RAM/CPU usage compared to Langfuse.
    * **Standardized:** Powered by OpenTelemetry; code remains portable to other backends.
    * **Zero-Config Local:** No mandatory databases or complex API keys for local dev.
    * **LangGraph Native:** Full visualization of cyclic graphs and nested spans.
* **Cons:** * **Ephemeral by Default:** Traces are stored in memory/local container storage unless persistence is explicitly configured.