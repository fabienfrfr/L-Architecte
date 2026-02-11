```text
==========================================================================================
    THE ARCHITECT - AGENTIC PIPELINE & SKAFFOLD INFRASTRUCTURE WORKFLOW
==========================================================================================

      LOCAL DEVELOPMENT (Host/DevContainer)           KUBERNETES RUNTIME (K3d Cluster)
    ┌────────────────────────────────────────┐      ┌───────────────────────────────────────┐
    │  WORKSPACE (VS Code / Fabien)          │      │  PODS & SERVICES (Namespace: AA)      │
    │                                        │      │                                       │
    │  [1. EDIT]                             │      │   ┌───────────────────────────────┐   │
    │  - apps/architect/*.py <───────────────┼──────┼──►│        POD: ARCHITECT         │   │
    │  - tests/*.py          (A) HOT RELOAD  │      │   │  (NiceGUI / FastAPI Server)   │   │
    │           │            (File Sync)     │      │   │                               │   │
    │           ▼                            │      │   │  [POST] Request ──┐           │   │
    │  ┌─────────────────┐                   │      │   └───────▲───────────│───────────┘   │
    │  │ SKAFFOLD ENGINE │                   │      │           │           │               │
    │  └────────┬────────┘                   │      │           │    (C) INTERNAL CALLS     │
    │           │                            │      │           │           │               │
    │           │              (B) DEPLOY    │      │   ┌───────▼───────┐   │   ┌───────────▼──┐
    │           └────────────────────────────┼──────┼──►│  POD: OLLAMA  │   └──►│ POD: PHOENIX │
    │                         (K8s Manifests)│      │   │  (Qwen2 0.6B)│       │ (Observability)
    │                                        │      │   └───────────────┘       └──────────────┘
    │  [2. INTERACTION]                      │      │                                       │
    │  ┌─────────────────────────────────┐   │      │   ┌───────────────────────────────┐   │
    │  │      BROWSER (localhost:8080)   │   │      │   │      SERVICE: ARCHITECT       │   │
    │  │ ------------------------------- │   │      │   │       (NodePort/LB)           │   │
    │  │ [GET]  <- Dashboard View        │◄──┼──────┼───┤                               │   │
    │  │ [POST] -> Chat / Agent Action   │───┼──────┼──►│  [PORT-FORWARD BY SKAFFOLD]   │   │
    │  └─────────────────────────────────┘   │      │   └───────────────────────────────┘   │
    │                                        │      └───────────────────────────────────────┘
    │  [3. VALIDATION]                       │                          │
    │  ┌───────────────────────────────────┐ │                          │
    │  │ COMMAND: "make test"              │ │                          │
    │  │                                   │ │                          │
    │  │ > kubectl exec architect          │ │                  (D) REMOTE TESTING          │
    │  │ > pytest tests/                   │─┼────────────────── (Runs inside Pod)          │
    │  └───────────────────────────────────┘ │                                              │
    └────────────────────────────────────────┘                                              │
                                                                                            │
==========================================================================================
LEGEND:
(A) HOT RELOAD : Skaffold syncs .py files instantly to the Pod without restart.
(B) DEPLOY    : Skaffold applies k3s-stack.yaml to ensure the environment is ready.
(C) INT. CALLS : The Architect app talks to Ollama (Inference) & Phoenix (Tracing).
(D) TESTING    : Pytest is triggered from DevContainer but executes inside the Pod.
==========================================================================================

```
