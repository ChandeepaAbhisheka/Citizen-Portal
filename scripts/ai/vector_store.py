from sentence_transformers import SentenceTransformer
import faiss  # type: ignore
import numpy as np
import json
import pickle
from typing import List, Dict, Tuple, Any
import os


class VectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize model and index settings"""
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Embedding size for MiniLM
        self.index: Any = None
        self.documents: List[Dict] = []

    # -------------------------------------------------------------
    # Generate embeddings
    # -------------------------------------------------------------
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of sentences."""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        return embeddings

    # -------------------------------------------------------------
    # Build FAISS index
    # -------------------------------------------------------------
    def build_index(self, documents: List[Dict]):
        """
        Build a FAISS vector index using a list of documents.
        Each document must contain a "text" field.
        """
        self.documents = documents
        texts = [doc["text"] for doc in documents]

        # Generate embeddings
        embeddings = self.create_embeddings(texts)

        # Create FAISS L2 index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)  # type: ignore

        print(f"[✔] FAISS Index built with {self.index.ntotal} vectors")

    # -------------------------------------------------------------
    # Search FAISS index
    # -------------------------------------------------------------
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents using FAISS.
        Returns a list of (document, distance).
        """
        query_embedding = self.create_embeddings([query])
        distances, indices = self.index.search(query_embedding, k)  # type: ignore

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))

        return results

    # -------------------------------------------------------------
    # Save FAISS index + documents
    # -------------------------------------------------------------
    def save(self, index_path: str = "data/faiss_index.bin",
             docs_path: str = "data/documents.pkl"):
        """Save index + docs to disk."""
        os.makedirs(os.path.dirname(index_path), exist_ok=True)

        faiss.write_index(self.index, index_path)
        with open(docs_path, "wb") as f:
            pickle.dump(self.documents, f)

        print(f"[✔] Index saved to {index_path}")
        print(f"[✔] Documents saved to {docs_path}")

    # -------------------------------------------------------------
    # Load FAISS index + documents
    # -------------------------------------------------------------
    def load(self, index_path: str = "data/faiss_index.bin",
             docs_path: str = "data/documents.pkl"):
        """Load index + docs from disk."""
        self.index = faiss.read_index(index_path)
        with open(docs_path, "rb") as f:
            self.documents = pickle.load(f)

        print("[✔] Vector store loaded successfully")


# -------------------------------------------------------------
# Build the index (run only if executed directly)
# -------------------------------------------------------------
if __name__ == "__main__":
    with open("data/processed_documents.json", "r") as f:
        documents = json.load(f)

    store = VectorStore()
    store.build_index(documents)
    store.save()
