from chromadb import Client


class ChromaDBManager:
    def __init__(self, host="chromadb", port=8000):
        self.client = Client(host=host, port=port)
        self.collection = self.client.create_collection("cdc_docs")

    def add_document(self, text: str, metadata: dict):
        self.collection.add(documents=[text], metadatas=[metadata])
