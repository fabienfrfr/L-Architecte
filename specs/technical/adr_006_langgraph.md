### # ADR 006: Usage of LangGraph for Agentic AI

**Status:** Accepted

**Decider:** Fabien Furfaro

**Context:** The project requires a framework capable of handling complex, non-linear agentic workflows. Standard "chains" are insufficient for agents that need to loop, reflect on their own work, or maintain state over long-running multi-step processes.

**Decision:** We will use **LangGraph** as the core orchestration engine. It allows us to define agents as a state machine (Nodes and Edges), providing fine-grained control over the "loop" and state persistence.

**Consequences:** * **Pros:** * **Cycles & Loops:** Native support for cyclic graphs, essential for agent self-correction.
* **Persistence:** Built-in "checkpointers" to save and resume agent states.
* **Fine-grained Control:** Unlike autonomous "black-box" agents, LangGraph allows manual intervention (Human-in-the-loop).

* **Cons:** * **Steeper Learning Curve:** More complex than simple LangChain sequences.
* **Boilerplate:** Requires explicit state and graph definition.
