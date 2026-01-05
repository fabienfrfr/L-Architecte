# <img src="./docs/architect_face.svg" width="25" alt="Architect Face"> AgenticArchitect

**AgenticArchitect** (or **TheArchitect**) is a local-first multi-agent system designed to transform raw client specifications into production-ready AI and Data solutions.

By leveraging **Stateful Graph Orchestration (LangGraph)** and high-performance local LLMs (like **NVIDIA Nemotron-3**), it automates the entire software development lifecycle (SDLC) from requirements analysis to SOLID code generation.

It features a high-performance web interface powered by **NiceGUI**. Demo on [thearchitect.dev](https://thearchitect.dev/) website ! (In progress)

![demo](/docs/global_demo.jpg)

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

## Deployment

### 1. Local (Docker Compose)

#### Prerequisites

- Docker and Docker Compose installed.
- NVIDIA GPU + NVIDIA Container Toolkit drivers.

#### Manual

Only on linux and not recommanded (only for testing) :

```bash
sudo apt-get install -y libgirepository-2.0-dev libcairo2-dev pkg-config gir1.2-gtk-3.0
git clone [https://github.com/fabienfrfr/AgenticArchitect.git](https://github.com/fabienfrfr/AgenticArchitect.git)
cd AgenticArchitect
pip install -r apps/architect/requirements.txt
python -m apps.architect.main
```

Access the app at [http://localhost:3000](http://localhost:3000). (or native mode)

#### Run

```bash
./scripts/deploy.sh local
```

Access the app at [http://localhost:3000](http://localhost:3000).

---

### 2. Cloud (AWS/GCP)

Migrate to OVH

#### Prerequisites

- AWS/GCP account with permissions.
- Terraform and Helm installed.

#### Run

```bash
./scripts/deploy.sh cloud
```

Get the frontend service URL:

```bash
kubectl get services frontend
```

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Copyright (c) 2025 **Fabien Furfaro** - [AgenticArchitect](https://github.com/fabienfrfr/AgenticArchitect)

Full license text available in the [LICENSE](./LICENSE) file with is notice in the [NOTICE](./NOTICE) file.