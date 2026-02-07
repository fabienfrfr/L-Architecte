import marimo

__generated_with = "0.19.6"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🏗️ TheArchitect: Minimalist R&D Lab
    **Author:** Fabien Furfaro
    **Project:** [AgenticArchitect](https://github.com/fabienfrfr/AgenticArchitect)

    > **Methodology:** Functional Testing (Playground Mode)
    > **Goal:** Testing ETL.

    We'll start by importing the necessary libraries for PDF processing, multimodal embedding, and graph visualization.
    """)
    return


@app.cell
def _():
    import os
    import subprocess
    import time

    import io
    import base64

    # --- Data & Maths ---
    import pandas as pd
    import numpy as np
    from fastembed import TextEmbedding, ImageEmbedding
    from sklearn.manifold import TSNE
    from sklearn.cluster import HDBSCAN
    from sklearn.metrics import pairwise_distances

    # --- PDF & Image Processing ---
    import fitz  # PyMuPDF

    # --- Graph & Visuals ---
    # import networkx as nx
    import plotly.graph_objects as go
    from IPython.display import display, HTML

    # --- Database
    from arango import ArangoClient

    # Path
    notebook_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(notebook_dir, "data", "Fiche_projet.pdf")
    return (
        ArangoClient,
        HDBSCAN,
        HTML,
        ImageEmbedding,
        TSNE,
        TextEmbedding,
        base64,
        display,
        fitz,
        go,
        io,
        np,
        pairwise_distances,
        pd,
        pdf_path,
        subprocess,
        time,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Extraction with Fitz
    """)
    return


@app.cell
def _(base64, display, fitz, pd, pdf_path):
    def extract_pdf_content(pdf_path: str):
        """Extracts text and images into a structured list of chunks."""
        extracted_chunks = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_num = page.number + 1

                # 1. Extract Text Blocks
                for _, _, _, _, text, _, b_type in page.get_text("blocks"):
                    clean_text = text.strip()
                    if b_type == 0 and len(clean_text) > 30:
                        extracted_chunks.append(
                            {
                                "chunk_id": f"p{page_num}_t{len(extracted_chunks)}",
                                "type": "text",
                                "content": clean_text,
                                "page": page_num,
                            }
                        )

                # 2. Extract Images
                for img_idx, img in enumerate(page.get_image_info(hashes=True)):
                    pix = page.get_pixmap(
                        clip=img["bbox"], matrix=fitz.Matrix(1.5, 1.5)
                    )
                    extracted_chunks.append(
                        {
                            "chunk_id": f"p{page_num}_i{img_idx}",
                            "type": "image",
                            "content": base64.b64encode(pix.tobytes("png")).decode(),
                            "page": page_num,
                            "dims": (pix.width, pix.height),
                        }
                    )
        return extracted_chunks

    # Execution
    raw_chunks = extract_pdf_content(pdf_path)
    df_raw = pd.DataFrame(raw_chunks)

    display(df_raw.drop(columns=["content"]).assign(preview=df_raw["content"].str[:]))
    return (df_raw,)


@app.cell
def _(HTML, df_raw, display):
    def html_display(pages):
        """Compact & pro dashboard with white background."""
        style = (
            "<style>"
            ".page-card{display:grid;grid-template-columns:1fr 1fr;gap:20px;"
            "border:1px solid #ddd;padding:15px;margin-bottom:15px;border-radius:8px;"
            "background:white;font-family:sans-serif;}"
            ".txt{font-size:13px;color:#333;max-height:300px;overflow-y:auto;}"
            "img{width:100%;border-radius:4px;}"
            ".title{grid-column:1/3;font-weight:bold;color:#3498db;border-bottom:1px solid #eee}"
            "</style>"
        )

        html = [style]
        for p in pages:
            if not (p["texts"] or p["images"]):
                continue

            txts = "".join(
                f"<p style='margin-bottom:8px'>• {t}</p>" for t in p["texts"]
            )
            imgs = "".join(
                f"<img src='data:image/png;base64,{img}'>" for img in p["images"]
            )

            html.append(f"""
            <div class="page-card">
                <div class="title">PAGE {p["page"]}</div>
                <div class="txt">{txts or "<i>No text</i>"}</div>
                <div>{imgs or "<i>No image</i>"}</div>
            </div>
            """)
        display(HTML("".join(html)))

    def html_display_from_df(dataframe):
        """Reconstructs the luxury view from the flat DataFrame."""
        pages_ids = sorted(dataframe["page"].unique())
        pages_to_display = []

        for p_id in pages_ids:
            page_df = dataframe[dataframe["page"] == p_id]
            pages_to_display.append(
                {
                    "page": p_id,
                    "texts": page_df[page_df["type"] == "text"]["content"].tolist(),
                    "images": page_df[page_df["type"] == "image"]["content"].tolist(),
                }
            )

        html_display(pages_to_display)

    html_display_from_df(df_raw)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Transformation with FastEmbed
    """)
    return


@app.cell
def _(ImageEmbedding, TextEmbedding, base64, df_raw, display, io, pd):
    def generate_multimodal_embeddings(df: pd.DataFrame):
        print("📥 Initializing Aligned CLIP Models (Qdrant)...")

        # Models are explicitly aligned in a 512D space
        text_model = TextEmbedding("Qdrant/clip-ViT-B-32-text")
        vision_model = ImageEmbedding("Qdrant/clip-ViT-B-32-vision")

        embeddings_list = []
        for _, row in df.iterrows():
            try:
                if row["type"] == "text":
                    vector = list(text_model.embed([str(row["content"])]))[0]
                else:
                    img_bytes = base64.b64decode(row["content"])
                    vector = list(vision_model.embed([io.BytesIO(img_bytes)]))[0]

                embeddings_list.append(
                    {
                        "chunk_id": row["chunk_id"],
                        "type": row["type"],
                        "page": row["page"],
                        "vector": vector,
                    }
                )
            except Exception as e:
                print(f"⚠️ Error processing {row['chunk_id']}: {e}")

        return pd.DataFrame(embeddings_list)

    df_vectors = generate_multimodal_embeddings(df_raw)
    display(df_vectors)
    return (df_vectors,)


@app.cell
def _(HDBSCAN, TSNE, df_vectors, display, np, pairwise_distances, pd):
    def compute_clusters_and_links(df: pd.DataFrame, top_k_neighbors: int = 3):
        """
        Reduces dimensionality for visualization and identifies semantic
        clusters and local bridges between nodes.
        """
        # 1. Dimensionality Reduction (t-SNE)
        embeddings = np.stack(df["vector"].values)
        normalized_embeddings = embeddings / np.linalg.norm(
            embeddings, axis=1, keepdims=True
        )

        # Initializing t-SNE with PCA to improve stability
        tsne_engine = TSNE(n_components=2, metric="cosine", init="pca", random_state=42)
        projections = tsne_engine.fit_transform(normalized_embeddings)
        df["x"], df["y"] = projections[:, 0], projections[:, 1]

        # 2. Density-Based Clustering (HDBSCAN)
        clusterer = HDBSCAN(
            min_cluster_size=2, cluster_selection_epsilon=0.05, copy=True
        )
        df["cluster"] = clusterer.fit_predict(projections)

        # 3. Fuzzy Relationship Extraction (KNN)
        distance_matrix = pairwise_distances(projections, metric="euclidean")
        neighborhood_data = []

        for i in range(len(df)):
            # Get indices of the K closest nodes (skipping the node itself at index 0)
            nearest_indices = np.argsort(distance_matrix[i])[1 : top_k_neighbors + 1]

            links = [
                {
                    "target_id": df.iloc[idx]["chunk_id"],
                    "weight": round(1 / (1 + distance_matrix[i, idx]), 3),
                    "target_cluster": df.iloc[idx]["cluster"],
                }
                for idx in nearest_indices
            ]
            neighborhood_data.append(links)

        df["relationships"] = neighborhood_data

        print(f"✅ Transformation complete: {len(df)} nodes processed.")
        return df

    # Execute Transformation
    df_graph = compute_clusters_and_links(df_vectors)
    display(df_graph[["chunk_id", "type", "cluster", "relationships"]])
    return (df_graph,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Visualization with NetworkX and Plotly
    """)
    return


@app.cell
def _(df_graph, go):
    def plot_architect_graph(df):
        fig = go.Figure()

        for _, row in df.iterrows():
            # Correction ici : on utilise 'relationships'
            for link in row["relationships"]:
                # On cherche via 'target_id'
                target_df = df[df["chunk_id"] == link["target_id"]]
                if target_df.empty:
                    continue

                target = target_df.iloc[0]
                is_bridge = row["cluster"] != target["cluster"]

                fig.add_trace(
                    go.Scatter(
                        x=[row["x"], target["x"], None],
                        y=[row["y"], target["y"], None],
                        mode="lines",
                        line=dict(
                            width=1.5 if is_bridge else 0.5,
                            color="orange" if is_bridge else "rgba(150,150,150,0.3)",
                            dash="dot" if is_bridge else "solid",
                        ),
                        showlegend=False,
                    )
                )

        # Nodes
        fig.add_trace(
            go.Scatter(
                x=df["x"],
                y=df["y"],
                mode="markers",
                marker=dict(
                    size=12,
                    color=df["cluster"],
                    colorscale="Viridis",
                    symbol=["square" if t == "image" else "circle" for t in df["type"]],
                    line_width=1,
                    showscale=True,
                ),
                text=df["chunk_id"],
                hoverinfo="text",
            )
        )

        fig.update_layout(
            title="TheArchitect: Multimodal Cluster Graph", showlegend=False
        )
        return fig

    fig_viz = plot_architect_graph(df_graph)
    fig_viz.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Load with ArangoDB
    """)
    return


@app.cell
def _(subprocess, time):
    def run_infra():
        # 1. Lancer le cluster et Arango
        print("🏗️  Building Cluster & Deploying Arango...")
        cmd = "make cluster && skaffold render | kubectl apply -l app=arangodb -f -"

        # On utilise run() car on veut attendre la fin
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Infrastructure ready.")
        else:
            print(f"❌ Error: {result.stderr}")
            return

        # 2. Port-forward en arrière-plan
        # On utilise Popen pour que ça ne soit pas bloquant
        print("🔗 Opening Tunnel (8529)...")
        subprocess.Popen(
            [
                "kubectl",
                "port-forward",
                "svc/arangodb",
                "8529:8529",
                "-n",
                "agentic-architect",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2)  # Petit délai pour laisser le tunnel s'établir
        print("🚀 ArangoDB is now accessible at http://localhost:8529")

    run_infra()
    return


@app.cell
def _(ArangoClient, df_graph):
    def load_to_arangodb(df, db_name="TheArchitect", password="your_password"):
        client = ArangoClient(hosts="http://localhost:8529")
        db = client.db(db_name, username="root", password=password)

        # 1. Setup Collections
        if not db.has_collection("Chunks"):
            db.create_collection("Chunks")
        if not db.has_collection("Relationships", edge=True):
            db.create_collection("Relationships", edge=True)

        chunks_coll = db.collection("Chunks")
        rel_coll = db.collection("Relationships")

        # 2. Upload Nodes (Chunks)
        # We exclude the raw vector for the standard document to keep it light
        nodes = df.drop(columns=["vector"]).to_dict("records")
        for node in nodes:
            node["_key"] = node["chunk_id"]
            chunks_coll.insert(node, overwrite=True)

        # 3. Upload Edges (Relationships)
        edges = []
        for _, row in df.iterrows():
            for rel in row["relationships"]:
                edges.append(
                    {
                        "_from": f"Chunks/{row['chunk_id']}",
                        "_to": f"Chunks/{rel['target_id']}",
                        "weight": rel["weight"],
                        "type": "bridge"
                        if row["cluster"] != rel["target_cluster"]
                        else "internal",
                    }
                )

        rel_coll.import_bulk(edges, overwrite=True)
        print(
            f"🚀 Successfully synced {len(nodes)} nodes and {len(edges)} edges to ArangoDB."
        )

    load_to_arangodb(df_graph)  # Décommenter pour exécuter
    return


if __name__ == "__main__":
    app.run()
