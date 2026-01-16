### # ADR 008: Fast Feedback Loop with Skaffold & DevContainers

**Status:** Accepted

**Decider:** Fabien Furfaro

**Context:** The traditional Kubernetes "Inner Loop" (Build -> Push -> Deploy) is too slow for Python development. Additionally, forcing every contributor to install specific versions of `kubectl`, `k3d`, and `skaffold` on their host machine creates "it works on my machine" issues.

**Decision:** We will use **Skaffold** managed through a **VS Code DevContainer**.

1. **Skaffold** handles the live synchronization of code into the cluster.
2. **DevContainer** automates the installation of the entire cloud-native toolchain and triggers the Skaffold lifecycle on startup.

**Consequences:**

* **Pros:** * **Zero-Install Onboarding:** A developer only needs Docker and VS Code. The DevContainer provides `skaffold`, `kubectl`, and `k3d` automatically.
* **Automated Workflow:** The `postStartCommand` in `devcontainer.json` launches the cluster and `skaffold dev` instantly.
* **Instant Feedback:** Python code changes are synced in <1s via Skaffold's file sync, without rebuilding images.
* **Unified Environment:** The DevContainer ensures that Skaffold always runs with the correct versions of dependencies.


* **Cons:** * **Resource Consumption:** Running a DevContainer + K3d + Skaffold requires at least 8GB of RAM.
* **Docker-in-Docker:** Requires mounting the Docker socket, which has security implications (acceptable in local dev).