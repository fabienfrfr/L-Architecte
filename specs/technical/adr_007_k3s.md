### # ADR 007: Local Kubernetes Infrastructure with K3d/K3s

**Status:** Accepted

**Decider:** Fabien Furfaro

**Context:** To ensure **TheArchitect** is "cloud-ready," we need an environment that mimics production (VPS/Cloud). Docker Compose lacks the service discovery, ingress management, and namespace isolation required for complex microservices (Ollama, Phoenix, Architect).

**Decision:** We adopt **K3d (K3s in Docker)** as the local infrastructure provider. It provides a full Kubernetes API while remaining extremely lightweight on system resources.

**Consequences:** * **Pros:** * **Environment Parity:** The exact same manifests (`k3s-stack.yaml`) work locally and on a production VPS.
* **Service Discovery:** Native Kubernetes DNS (e.g., `http://ollama:11434`) instead of fragile port-mapping.
* **Isolation:** Use of Namespaces to separate the agentic stack from other tools.

* **Cons:** * **Overhead:** Slightly higher RAM usage than pure Docker.
* **Complexity:** Requires knowledge of `kubectl` and Kubernetes concepts.
