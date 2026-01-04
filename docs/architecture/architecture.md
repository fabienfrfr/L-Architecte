# AgenticArchitect
## Overview
A local-first multi-agent system for AI/ML projects.

### Components
- **Analyst Agent**: CDC analysis.
- **Architect Agent**: C4 diagrams, ADRs.
- **Engineer Agent**: SOLID code generation.

### Architecture Diagram
```mermaid
graph TD
    A[Client] --> B[FastAPI]
    B --> C[Analyst Agent]
    B --> D[Architect Agent]
    B --> E[Engineer Agent]
    C --> F[ChromaDB]
    D --> G[ADR]
    E --> H[SOLID Code]
```
