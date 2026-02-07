import re
import fitz  # PyMuPDF
from fastembed import TextEmbedding
from arango import ArangoClient
import numpy as np


class ETLMapper:
    """
    Lightweight Semantic ETL for TheArchitect.
    Uses ONNX-based embeddings for entity recognition.
    """

    def __init__(self):
        # Extremely light model (~15MB on disk)
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

        self.client = ArangoClient(hosts="http://localhost:8529")
        self.db = self.client.db("TheArchitect", username="root", password="password")

        # Reference embeddings for our categories
        self.categories = {
            "software": "software programming tool library",
            "infrastructure": "cloud server network hardware",
            "protocol": "communication protocol interface",
        }
        self._category_vectors = {
            k: list(self.model.embed([v]))[0] for k, v in self.categories.items()
        }

    def _extract(self, file_path):
        doc = fitz.open(file_path)
        pages_data = []

        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages_data.append({"page_num": i + 1, "content": text})

        doc.close()
        return pages_data

    def _transform(self, raw_pages):
        data = []
        for page in raw_pages:
            text = " ".join(page["content"].split())
            words = list(
                set(re.findall(r"\b\w{3,}\b", text))
            )  # Extraction simple des mots candidats

            entities = []
            if words:
                # Embed each candidate word
                word_embeddings = list(self.model.embed(words))

                for i, word_vec in enumerate(word_embeddings):
                    for label, cat_vec in self._category_vectors.items():
                        # Simple cosine similarity
                        score = np.dot(word_vec, cat_vec) / (
                            np.linalg.norm(word_vec) * np.linalg.norm(cat_vec)
                        )
                        if score > 0.8:  # Threshold for semantic match
                            entities.append({"text": words[i], "label": label})

            data.append({"text": text, "page": page["page_num"], "entities": entities})
        return data

    def _load(self, data, doc_name):
        # Persistence logic remains the same
        chunks = [{"text": d["text"], "doc": doc_name, "page": d["page"]} for d in data]
        self.db.collection("Chunks").import_bulk(chunks)

        for d in data:
            for ent in d["entities"]:
                key = ent["text"].lower()
                if not self.db.collection("Entities").has(key):
                    self.db.collection("Entities").insert(
                        {"_key": key, "name": ent["text"], "type": ent["label"]}
                    )
