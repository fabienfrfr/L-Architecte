# ADR 001: ArangoDB as Multi-Model Knowledge Graph

**Status:** Superseded (Replaces ChromaDB)

**Decider:** Fabien Furfaro

**Context:** Initial RAG requirements were limited to simple vector search (ChromaDB). However, **AgenticArchitect** needs to model complex relationships between code, requirements, and agent states. Managing separate databases for vectors (Chroma), documents (JSON), and graphs (Relationships) introduces unnecessary architectural fragmentation and high operational overhead.

**Decision:** We will use **ArangoDB** as the unified multi-model database for the entire ecosystem.

1. **Unified Storage**: All project data (Source code, Metadata, Embeddings) will reside in a single ArangoDB instance.
2. **ArangoSearch**: We will leverage the `Integrated Vector Search` and `Inverted Indexes` for hybrid retrieval (BM25 + HNSW).
3. **Graph Traversal**: Relationships between files (imports), agents (task history), and requirements (REQ-ID) will be modeled as Edges.
4. **Deployment**: Deployed via Helm within the K3d cluster and managed by Skaffold.

**Consequences:**

* **Pros:**
* **Relational Intelligence:** Agents can traverse the graph to understand code dependencies, not just text similarity.
* **Hybrid RAG:** Combines vector search with structured AQL queries for 100% precision on specific IDs (e.g., `REQ-OLLAMA`).
* **Future-Proof:** No need to migrate data later when adding complex agent memory or lineage tracking.
* **Infrastructure Consolidation:** One service to manage in K8s instead of three different database types.


* **Cons:**
* **Increased Footprint:** Requires ~512MB-1GB RAM, increasing the local cluster's resource pressure.
* **Query Complexity:** Requires learning AQL (ArangoDB Query Language) for advanced graph traversals.
* **Setup Overhead:** Requires persistent volume management and specific ArangoSearch index configuration.