import pypdfium2 as pdfium
import spacy
from arango import ArangoClient

# Load lightweight French/English model
# python -m spacy download fr_core_news_sm
nlp = spacy.load("fr_core_news_sm", disable=["lemmatizer", "attribute_ruler"])

class ETLMapper:
    def __init__(self, db_auth):
        self.client = ArangoClient(hosts='http://localhost:8529')
        self.db = self.client.db('TheArchitect', username='root', password='password')

    # --- [E]XTRACT ---
    def _extract(self, file_path):
        """Extracts raw text from PDF using pypdfium2 (very fast)."""
        doc = pdfium.PdfDocument(file_path)
        pages = []
        for i in range(len(doc)):
            page = doc.get_page(i)
            text = page.get_textpage().get_text_range()
            pages.append({"page_num": i + 1, "content": text})
        return pages

    # --- [T]RANSFORM ---
    def _transform(self, raw_pages):
        """Cleans text and extracts technical entities via spaCy."""
        structured_data = []
        for page in raw_pages:
            content = page["content"]
            # Basic cleaning
            clean_text = " ".join(content.split())
            
            # NER (Entity Recognition)
            doc = nlp(clean_text)
            entities = [{"text": ent.text, "label": ent.label_} 
                        for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "MISC"]]
            
            structured_data.append({
                "text": clean_text,
                "metadata": {"page": page["page_num"]},
                "entities": entities
            })
        return structured_data

    # --- [L]OAD ---
    def _load(self, data, doc_name):
        """Loads chunks and entities into ArangoDB collections."""
        # 1. Store Chunks
        self.db.collection('Chunks').import_bulk(
            [{"text": d['text'], "doc": doc_name, "page": d['metadata']['page']} for d in data]
        )
        # 2. Store Entities (Simplified logic)
        for d in data:
            for ent in d['entities']:
                key = ent['text'].replace(" ", "_").lower()
                if not self.db.collection('Entities').has(key):
                    self.db.collection('Entities').insert({"_key": key, "name": ent['text']})

    def run(self, file_path):
        """The main entry point for the ETL process."""
        print(f"🚀 Starting ETL for {file_path}")
        raw = self._extract(file_path)
        transformed = self._transform(raw)
        self._load(transformed, os.path.basename(file_path))
        print("✅ ArangoDB Graph Updated.")