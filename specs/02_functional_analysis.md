# Functional Analysis

## Main Functions (MF)

| ID             | Function             | Goal                                             |
| :------------- | :------------------- | :----------------------------------------------- |
| **MF-1** | Requirement Analysis | Extract SMART criteria from unstructured text.   |
| **MF-2** | Architectural Design | Generate C4 models and ADR justifications.       |
| **MF-3** | Engineering          | Produce SOLID Python code and Pytest suites.     |
| **MF-4** | Orchestration        | Manage the state and transitions between agents. |

## Constraint Functions (CF)

| ID             | Constraint   | Requirement                                                |
| :------------- | :----------- | :--------------------------------------------------------- |
| **CF-1** | Sovereignty  | 100% Offline execution (No Cloud APIs).                    |
| **CF-2** | Hardware     | Must run on consumer GPUs (VRAM optimized).                |
| **CF-3** | Traceability | Every file generated must have a clear ownership metadata. |
| **CF-4** | Robustness   | System must retry on LLM JSON parsing failures.            |
