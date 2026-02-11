# ADR 004: Demo Deployment on OVHcloud (CPU-Only)

**Status:** Superseded

**Decider:** Fabien Furfaro

### 1. Context

The demo is being moved to an OVHcloud VPS without GPU acceleration. The deployment must be automated, secure, and compatible with CPU-only inference.

### 2. Decision

* **Reverse Proxy**: Use **Traefik** instead of Nginx. Traefik will act as the entry point, automatically detecting Docker containers and managing Let's Encrypt certificates via labels.
* **Model Selection**: Switch to `qwen3:0.6b` (or similar light versions) to allow the **PMAgent** and **AnalystAgent** to run on CPU without timing out the UI.
* **Automation**: Use **SSH** for remote deployment and add a target to the `Makefile` for one-click updates.

### 3. Consequences

* **Pros**: Zero-config SSL, automated service discovery, and lower overhead than Nginx.
* **Cons**: Lower inference quality compared to Nemotron-3, but sufficient for a workflow demo.
