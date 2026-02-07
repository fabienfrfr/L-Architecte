# Functional Specifications: AgenticArchitect

**Author:** Fabien Furfaro (@fabienfrfr)  
**Status:** Draft / Technical Baseline  
**Date:** 2025-12-31

## 1. System Intent (The "Why")
The primary goal of **AgenticArchitect** (TheArchitect) is to automate the transformation of unstructured client requirements into a structured, production-ready software architecture and codebase, while ensuring 100% data sovereignty through local-first execution.

---

## 2. Functional Analysis (APTE Framework)

### 2.1 Main Functions (MF)
These represent the core value added by the agentic bus.

| ID | Function Name | Description | Acceptance Criteria |
|:---|:---|:---|:---|
| **MF-1** | **Requirement Extraction** | Analyze raw text/PDF to identify SMART objectives and gaps. | Returns a structured JSON charter with `is_smart` boolean. |
| **MF-2** | **Technical Mapping** | Map business needs to specific architectural patterns (C4, ADR). | Generates valid Mermaid diagram code and markdown ADRs. |
| **MF-3** | **SOLID Code Generation** | Produce Python code following SOLID principles and TDD. | Code must be syntactically correct and include a `pytest` suite. |
| **MF-4** | **Behavioral Validation** | Validate generated code against original functional features. | Execution of `pytest-bdd` scenarios returns green. |

### 2.2 Constraint Functions (CF)
These define the boundaries and mandatory technical limits of the system.

| ID | Constraint Category | Description | Technical Metric |
|:---|:---|:---|:---|
| **CF-1** | **Local-First (Sovereignty)** | No data shall leave the local host or private cloud network. | Use of `OLLAMA_URL` with local inference only. |
| **CF-2** | **Determinism & Traceability** | Every architectural choice must be justified and logged. | Every `final_code` must be linked to a specific `ADR`. |
| **CF-3** | **Self-Healing (Robustness)** | The system must handle LLM hallucinations or parsing errors. | Implement a `retry_router` (max 3 attempts). |
| **CF-4** | **Platform Independence** | The core logic must be installable via Docker on Linux/Windows. | Docker image must include system libraries (GTK/Cairo). |
| **CF-5** | **Hardware Efficiency** | Must run on consumer/prosumer GPUs within VRAM limits. | Quantized models (e.g., Nemotron-3 Nano) must be used. |

---

## 3. Operational Modes

### 3.1 Mode: Development (Local)
* **Target**: Local workstation (Lenovo/Linux).
* **UI**: Native window (if `NICEGUI_NATIVE=True`) or browser.
* **LLM**: `nemotron-3-nano:30b`.

### 3.2 Mode: Testing (CI/CD)
* **Target**: GitHub Actions / Headless.
* **UI**: Disabled (Headless testing).
* **LLM**: `gemma3:270m` (ultra-lightweight for speed).

---

## 4. Requirement Traceability Matrix (Draft)

* **SMART Validation** → Covered by `PMAgent` and `pm_node`.
* **C4 Diagramming** → Covered by `ArchitectAgent`.
* **SOLID Scaffolding** → Covered by `EngineerAgent`.
* **Local RAG** → Covered by `ChromaDBManager`.