# <img src="./docs/architect_face.svg" width="25" alt="Architect Face"> AgenticArchitect

[![Codeberg](https://img.shields.io/badge/Codeberg-2185d0?style=for-the-badge&logo=gitea&logoColor=white)](https://codeberg.org/fabienfrfr/AgenticArchitect)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/fabienfrfr/AgenticArchitect)

**AgenticArchitect** (or **TheArchitect**) is a local-first multi-agent system designed to transform raw client specifications into production-ready AI and Data solutions.

By leveraging **Stateful Graph Orchestration (LangGraph)** and high-performance local LLMs (like **NVIDIA Nemotron-3**), it automates the entire software development lifecycle (SDLC) from requirements analysis to SOLID code generation.

It features a web interface powered by **NiceGUI**. Demo on [thearchitect.dev](https://thearchitect.dev/) website ! (In progress)

![demo](/docs/thearchitect-banner.jpg)

## 🏗️ Core Architecture (The Swimlane)

The system follows a strict automated workflow based on an agentic bus:

1. **Project Manager Agent**: Validates SMART requirements and identifies gaps.
2. **Data Analyst Agent**: Performs EDA and synthetic data generation.
3. **Architect Agent**: Designs C4 Diagrams and Decision Records (ADR).
4. **Engineer Agent**: Produces TDD-backed, SOLID-compliant code.

While general-purpose agents like Skywork, Manus, or Genspark excel at rapid task execution, **AgenticArchitect** focuses on the craft of software engineering. It is not just a tool for generating results; it is a framework for building sustainable architecture, enforcing rigorous methodologies, and maintaining total sovereignty over your local infrastructure. This approach, designed to automate software design, shares a philosophical kinship with the [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD), but focuses on a native, local, autonomous, and simplified implementation for immediate execution.

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


## 🚀 Local Deployment

This project uses a containerized architecture managed by Docker Compose. The infrastructure includes **Traefik** (reverse proxy), **Arize Phoenix** (observability), **Ollama** (LLM engine), and the **AgenticArchitect** application.

### 📋 Prerequisites

* **Docker** and **Docker Compose** installed.
* **Ollama** running on your host or via the provided container.

### 🛠️ One-Command Setup


```bash
# Navigate to the project root
cd ~/AgenticArchitect

# Start services using the deployment profile
docker compose -f infra/services/docker-compose.yml up -d --build

```

### 🔍 Service Access

| Service |  Local/Internal URL |
| --- | --- | 
| **TheArchitect UI** | `http://localhost:8080` |
| **Arize Phoenix** | `http://localhost:6006` |
| **Ollama API** | `http://localhost:11434` |


## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Copyright (c) 2025 **Fabien Furfaro** - [AgenticArchitect](https://github.com/fabienfrfr/AgenticArchitect)

Full license text available in the [LICENSE](./LICENSE) file with is notice in the [NOTICE](./NOTICE) file.