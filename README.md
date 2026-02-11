# <img src="./docs/architect_face.svg" width="25" alt="Architect Face"> L-Architecte

[![Codeberg](https://img.shields.io/badge/Codeberg-2185d0?style=for-the-badge&logo=gitea&logoColor=white)](https://codeberg.org/fabienfrfr/L-Architecte)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/fabienfrfr/L-Architecte)

> **🚧 WORK IN PROGRESS:**  Moving from LangGraph to **Pydantic AI + Pydantic Graph**. Currently refactoring the orchestration layer to leverage native Python schemas and static type-checking for more predictable agentic flows.

**L-Architecte** (or **TheArchitect**) is a local-first multi-agent system designed to transform raw client specifications into production-ready AI and Data solutions.

By leveraging **Stateful Graph Orchestration (~~LangGraph~~ Pydantic AI & Graph)** and high-performance local LLMs (like **NVIDIA Nemotron-3**), it automates the entire software development lifecycle (SDLC) from requirements analysis to SOLID code generation.

It features a web interface powered by **NiceGUI**. Demo on [thearchitect.dev](https://thearchitect.dev/) website ! (In progress)

![demo](/docs/thearchitect-banner.jpg)

## 🏗️ Core Architecture (The Swimlane)

The system follows a strict automated workflow based on an agentic bus:

1. **Project Manager Agent**: Validates SMART requirements and identifies gaps.
2. **Data Analyst Agent**: Performs EDA and synthetic data generation.
3. **Architect Agent**: Designs C4 Diagrams and Decision Records (ADR).
4. **Engineer Agent**: Produces TDD-backed, SOLID-compliant code.

While general-purpose agents like Skywork, Manus, or Genspark excel at rapid task execution, **AgenticArchitect** focuses on the craft of software engineering. It is not just a tool for generating results; it is a framework for building sustainable architecture, enforcing rigorous methodologies, and maintaining total sovereignty over your local infrastructure. This approach, designed to automate software design, shares a philosophical kinship with the [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) or [MetaGPT](https://github.com/FoundationAgents/MetaGPT), but focuses on a native, local, autonomous, and simplified implementation for immediate execution.


---

### 🎯 Roadmap: The Path to "Master Architect"

One of the core goals of **AgenticArchitect** is to achieve **Self-Evolution**. **AgenticArchitect** is also a personal laboratory for mastering cloud architecture standards. The goal is to align the agents' outputs with official certification requirements to ensure industrial-grade designs.

* **Current focus:** Training the agents to respect **OVHcloud Solutions Architect** standards (vRack isolation, OVH Bare Metal API, OpenStack Cloud, S3 compliance, and sovereign data management).
* **Methodology:** Implementing **iSAQB** agnostic patterns to move beyond simple "code generation" toward true system engineering (SoC, DRY, KISS and SOLID).


## 🔍 Related Research & Agentic Tools

Here are some useful resources and projects for deep research and agentic AI systems:

- [GPT Researcher – Open deep research agent for web + local documents](https://github.com/assafelovic/gpt-researcher)
- [AutoAgent – Fully-Automated and Zero-Code Framework for LLM Agents (arXiv)](https://arxiv.org/abs/2502.05957v3)
- [ASTA – Accelerating science through trustworthy agentic AI (Allen Institute)](https://allenai.org/blog/asta)
- [Agent Laboratory – Interactive environment for multi-agent scientific research](https://agentlaboratory.github.io/)

Other relevant resources:

- [LangGraph – Framework for building stateful, multi-actor LLM applications](https://github.com/langchain-ai/langgraph)
- [AutoGen – Multi-agent conversation framework for LLM applications](https://github.com/microsoft/autogen)
- [Elicit – AI research assistant for literature review and scientific workflows](https://elicit.org/)
- [Claude – Agents Inspirations](https://github.com/VoltAgent/awesome-claude-code-subagents)

## ⚡ Zero-Touch Startup (CLI-only)

Designed for speed. This workflow installs the tools, builds the cluster, and launches the agents in one go.

```bash
git clone https://github.com/fabienfrfr/AgenticArchitect
cd AgenticArchitect

# The 'Golden Path' to a ready-to-code environment:
make install && make cluster && make setup-dev && skaffold dev

```

### What happens under the hood?

1. **`make install`**: Automatically detects your OS and installs `uv`, `k3d`, `kubectl`, and `skaffold`.
2. **`make cluster`**: Provisions a local K3d cluster with optimized port-forwarding.
3. **`make setup-dev`**: Uses **UV** to sync Python dependencies and pre-pulls light **Qwen 3:0.6B** into the cluster.
4. **`skaffold dev`**: Starts continuous hot-reload. Any file change is instantly reflected in the running pods.

## 🛠️ The Power Tools

| Tool | Role | Why it's here |
| --- | --- | --- |
| **K3d / K3s** | Orchestration | Industrial scale for local agents. |
| **Skaffold** | Deployment | Zero-wait development loop. |
| **Pydantic AI** | Agent Framework | **Type-safe** LLM orchestration & structured validation. |
| **UV** | Python Manager | 10x faster than pip/poetry. |
| **Ollama** | LLM Engine | Total data sovereignty with **Qwen 3:0.6B**. |
| **Ruff** | Code Quality | Blazing fast SOLID enforcement. |


## 🔍 Service Access

Once the stack is up, all services are mapped to your localhost:

| Service | Local URL | Description |
| --- | --- | --- |
| **TheArchitect UI** | `http://localhost:8080` | NiceGUI Control Panel |
| **Arize Phoenix** | `http://localhost:6006` | Traces & Observability |
| **Ollama API** | `http://localhost:11434` | Local Inference Engine |


## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Copyright (c) 2026 **Fabien Furfaro** - Full license text available in the [LICENSE](./LICENSE) file with is notice in the [NOTICE](./NOTICE) file.