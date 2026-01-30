import marimo

__generated_with = "0.19.7"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🏗️ TheArchitect: Minimalist R&D Lab
    **Author:** Fabien Furfaro
    **Project:** [AgenticArchitect](https://github.com/fabienfrfr/AgenticArchitect)

    > **Methodology:** Functional Testing (Playground Mode)
    > **Goal:** Testing ETL.
    """)
    return


@app.cell
def _():
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
    import networkx as nx
    import plotly.graph_objects as go
    from IPython.display import display, HTML
    return (
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
        nx,
        pairwise_distances,
        pd,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Extraction with Fitz
    """)
    return


@app.cell
def _(base64, display, fitz, pd):
    def extract_for_graph(pdf_path: str):
        """Extracts everything into a flat list of chunks for Graph/Embedding."""
        chunks = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                p_id = page.number + 1
            
                # Text blocks
                for _, _, _, _, text, _, b_type in page.get_text("blocks"):
                    content = text.strip()
                    if b_type == 0 and len(content) > 30:
                        chunks.append({
                            "id": f"p{p_id}_t{len(chunks)}",
                            "type": "text",
                            "content": content,
                            "page": p_id
                        })
            
                # Images
                for i_idx, img in enumerate(page.get_image_info(hashes=True)):
                    pix = page.get_pixmap(clip=img["bbox"], matrix=fitz.Matrix(1.5, 1.5))
                    chunks.append({
                        "id": f"p{p_id}_i{i_idx}",
                        "type": "image",
                        "content": base64.b64encode(pix.tobytes("png")).decode(),
                        "page": p_id,
                        "dims": [pix.width, pix.height]
                    })
        return chunks

    # --- Transformation en DataFrame ---
    raw_data = extract_for_graph("data/Fiche_projet.pdf")
    df = pd.DataFrame(raw_data)

    # Visualisation rapide du tableau (sans saturer le notebook)
    display(df.drop(columns=['content']).assign(preview=df['content'].str[:]))
    return (df,)


@app.cell
def _(HTML, df, display):
    def luxury_display(pages):
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
            if not (p["texts"] or p["images"]): continue
        
            txts = "".join(f"<p style='margin-bottom:8px'>• {t}</p>" for t in p["texts"])
            imgs = "".join(f"<img src='data:image/png;base64,{img}'>" for img in p["images"])
        
            html.append(f"""
            <div class="page-card">
                <div class="title">PAGE {p['page']}</div>
                <div class="txt">{txts or '<i>No text</i>'}</div>
                <div>{imgs or '<i>No image</i>'}</div>
            </div>
            """)
        display(HTML("".join(html)))

    def luxury_display_from_df(dataframe):
        """Reconstructs the luxury view from the flat DataFrame."""
        pages_ids = sorted(dataframe['page'].unique())
        pages_to_display = []
    
        for p_id in pages_ids:
            page_df = dataframe[dataframe['page'] == p_id]
            pages_to_display.append({
                "page": p_id,
                "texts": page_df[page_df['type'] == 'text']['content'].tolist(),
                "images": page_df[page_df['type'] == 'image']['content'].tolist()
            })
    
        luxury_display(pages_to_display)

    # --- Exécution ---
    if 'df' in locals() or 'df' in globals():
        luxury_display_from_df(df)
    else:
        print("Erreur : Le DataFrame 'df' n'a pas été trouvé. Lance la cellule d'extraction d'abord !")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Transformation with FastEmbed
    """)
    return


@app.cell
def _(ImageEmbedding, TextEmbedding):
    # 1. Lister les modèles de chaque catégorie
    text_models = {m["model"] for m in TextEmbedding.list_supported_models()}
    image_models = {m["model"] for m in ImageEmbedding.list_supported_models()}

    # 2. Trouver l'intersection (les modèles multimodaux complets)
    multimodal_models = text_models.intersection(image_models)

    # 3. Afficher le résultat proprement
    if multimodal_models:
        print("✅ Modèles supportant TEXTE et IMAGE (Alignés) :")
        for model in multimodal_models:
            print(f" - {model}")
    else:
        print("❌ Aucun modèle n'est listé dans les deux catégories avec le même nom.")

    # Bonus : Voir si Jina est là sous un autre nom
    print("\n🔍 Recherche de model dans le texte :", [m for m in text_models ])
    print("🔍 Recherche de model dans l'image :", [m for m in image_models])
    return


@app.cell
def _(ImageEmbedding, TextEmbedding, base64, df, display, io, pd):
    def compute_multimodal_vectors(df: pd.DataFrame):
        print("📥 Loading Aligned CLIP Pair (Qdrant Standard)...")
    
        # On utilise la paire de modèles officiels de Qdrant
        # Ils sont parfaitement alignés (Espace 512D)
        t_model = TextEmbedding("Qdrant/clip-ViT-B-32-text")
        i_model = ImageEmbedding("Qdrant/clip-ViT-B-32-vision")
    
        results = []
        for _, row in df.iterrows():
            try:
                content = row["content"]
                if not content: continue
                
                if row["type"] == "text":
                    # TextEmbedding ne confondra jamais ton texte avec un fichier
                    vector = list(t_model.embed([str(content)]))[0]
                else:
                    # ImageEmbedding gère les bytes sans souci
                    img_data = base64.b64decode(content)
                    vector = list(i_model.embed([io.BytesIO(img_data)]))[0]
            
                results.append({
                    "id": row["id"],
                    "type": row["type"],
                    "page": row["page"],
                    "vector": vector,
                    "dim": len(vector)
                })
            except Exception as e:
                print(f"⚠️ Erreur sur {row['id']} : {e}")

        return pd.DataFrame(results)

    # --- Exécution ---
    v_df = compute_multimodal_vectors(df)
    display(v_df)
    return (v_df,)


@app.cell
def _(HDBSCAN, TSNE, display, np, pairwise_distances, v_df):
    def build_sklearn_fuzzy_clusters(v_df, top_k_links=3):
        print("🚀 Running TSNE + Fuzzy Links Mode...")
    
        # 1. Préparation & Normalisation
        X = np.stack(v_df['vector'].values)
        X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)
    
        # 2. TSNE : On réduit à 2D
        tsne = TSNE(n_components=2, metric='cosine', init='pca', random_state=42)
        coords_2d = tsne.fit_transform(X_norm)
        v_df['x'], v_df['y'] = coords_2d[:, 0], coords_2d[:, 1]
    
        # 3. HDBSCAN pour le cluster principal (ton point d'ancrage)
        clusterer = HDBSCAN(min_cluster_size=2, cluster_selection_epsilon=0.05).fit(coords_2d)
        v_df['cluster'] = clusterer.labels_

        # 4. CALCUL DES LIENS MULTIPLES (C'est ici que ça devient smart)
        # On calcule la distance entre chaque point
        dist_matrix = pairwise_distances(coords_2d, metric='euclidean')
    
        fuzzy_links = []
        for i in range(len(v_df)):
            # Pour chaque point, on trouve les K voisins les plus proches (excluant lui-même)
            # On trie les indices par distance
            nearest_indices = np.argsort(dist_matrix[i])[1:top_k_links+1]
        
            # On stocke les IDs des voisins et la force du lien (inverse de la distance)
            links = []
            for idx in nearest_indices:
                strength = 1 / (1 + dist_matrix[i, idx]) # Score entre 0 et 1
                links.append({
                    'to': v_df.iloc[idx]['id'],
                    'strength': round(strength, 3),
                    'target_cluster': v_df.iloc[idx]['cluster']
                })
            fuzzy_links.append(links)
    
        v_df['neighbors'] = fuzzy_links
    
        # 5. Sauvetage rapide des clusters -1 (juste pour la couleur dans le graphe)
        if -1 in v_df['cluster'].values:
            for i, row in v_df.iterrows():
                if row['cluster'] == -1:
                    # On prend le cluster du voisin le plus proche qui n'est pas à -1
                    for link in row['neighbors']:
                        if link['target_cluster'] != -1:
                            v_df.at[i, 'cluster'] = link['target_cluster']
                            break

        print(f"✅ Graphe prêt avec {top_k_links} liens potentiels par nœud.")
        return v_df

    # --- Exécution ---
    v_df_ = build_sklearn_fuzzy_clusters(v_df)
    # Regarde la colonne 'neighbors' pour ta maquette !
    display(v_df_[['id', 'type', 'cluster', 'neighbors']])
    return (v_df_,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Visualization with NetworkX and Plotly
    """)
    return


@app.cell
def _(go, nx, v_df_):
    def visualize_fuzzy_architect_graph(v_df):
        G = nx.Graph()
    
        # 1. Création des Nœuds
        for _, row in v_df.iterrows():
            G.add_node(row['id'], 
                       type=row['type'], 
                       cluster=row['cluster'],
                       text=f"ID: {row['id']}<br>Type: {row['type']}<br>Cluster: {row['cluster']}",
                       pos=(row['x'], row['y']))

        # 2. Préparation des traces pour les Arêtes
        # On va séparer les liens internes (même cluster) et les ponts (clusters différents)
        inner_x, inner_y = [], []
        bridge_x, bridge_y = [], []

        for _, row in v_df.iterrows():
            x0, y0 = row['x'], row['y']
            current_cluster = row['cluster']
        
            for link in row['neighbors']:
                # On cherche les coordonnées de la cible (le 'to')
                target_row = v_df[v_df['id'] == link['to']]
                if not target_row.empty:
                    x1, y1 = target_row.iloc[0]['x'], target_row.iloc[0]['y']
                    target_cluster = target_row.iloc[0]['cluster']
                
                    if target_cluster == current_cluster:
                        inner_x.extend([x0, x1, None])
                        inner_y.extend([y0, y1, None])
                    else:
                        bridge_x.extend([x0, x1, None])
                        bridge_y.extend([y0, y1, None])

        # Trace 1: Liens internes (Gris discret)
        inner_trace = go.Scatter(
            x=inner_x, y=inner_y,
            line=dict(width=0.8, color='rgba(150,150,150,0.4)'),
            hoverinfo='none', mode='lines', name='Inner Cluster')

        # Trace 2: LES PONTS (Orange/Rouge pour qu'ils soient visibles)
        bridge_trace = go.Scatter(
            x=bridge_x, y=bridge_y,
            line=dict(width=1.5, color='orange', dash='dot'),
            hoverinfo='none', mode='lines', name='Cross-Cluster Bridge')

        # 3. Tracé des Nœuds
        node_x, node_y, node_color, node_symbol, node_hover = [], [], [], [], []
        for node in G.nodes():
            x, y = G.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)
            node_color.append(G.nodes[node]['cluster'])
            node_symbol.append('square' if G.nodes[node]['type'] == 'image' else 'circle')
            node_hover.append(G.nodes[node]['text'])

        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers', hoverinfo='text',
            text=node_hover,
            marker=dict(
                showscale=True, colorscale='Viridis', color=node_color,
                size=14, symbol=node_symbol, line_width=1.5,
                colorbar=dict(title="Cluster ID")))

        # 4. Layout
        fig = go.Figure(data=[inner_trace, bridge_trace, node_trace],
                     layout=go.Layout(
                        title=dict(text='TheArchitect: Visualisation des Ponts Inter-Clusters'),
                        showlegend=True,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=60),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
        return fig

    # --- Affichage ---
    fig = visualize_fuzzy_architect_graph(v_df_)
    fig.show()

    return


@app.cell
def _(HTML, Markdown, df, display, v_df_):
    def inspect_cluster(df, cluster_id):
        # Filtrage
        cluster_data = df[df['cluster'] == cluster_id].copy()
    
        if cluster_data.empty:
            return Markdown(f"### ⚠️ Cluster {cluster_id} est vide.")
    
        html_output = f"<h3>🔍 Inspection du Cluster {cluster_id} ({len(cluster_data)} éléments)</h3>"
        html_output += "<table style='width:100%; border-collapse: collapse;'>"
        html_output += "<tr style='background-color: #333; color: white;'><th>Type</th><th>ID</th><th>Contenu / Aperçu</th></tr>"
    
        for _, row in cluster_data.iterrows():
            content = ""
            if row['type'] == 'text':
                # On affiche les 200 premiers caractères du texte
                content = f"<div style='font-size: 0.9em;'>{row.get('content', 'Texte non chargé')[:200]}...</div>"
            elif row['type'] == 'image':
                # Si tu as stocké l'image en base64 ou le path
                if 'image_base64' in row:
                    content = f"<img src='data:image/png;base64,{row['image_base64']}' style='height:100px; border-radius:5px;'/>"
                else:
                    content = "🖼️ [Image Maquette]"
        
            html_output += f"<tr style='border-bottom: 1px solid #ddd;'>"
            html_output += f"<td><b>{row['type'].upper()}</b></td>"
            html_output += f"<td><code>{row['id']}</code></td>"
            html_output += f"<td>{content}</td></tr>"
    
        html_output += "</table>"
        return HTML(html_output)

    # Utilisation manuelle :
    final_df_ = v_df_.merge(df[['id', 'content']], on='id', how='left')
    display(inspect_cluster(final_df_, cluster_id=5))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Load with ArangoDB
    """)
    return


@app.cell
def _():
    c = 3
    return


if __name__ == "__main__":
    app.run()
