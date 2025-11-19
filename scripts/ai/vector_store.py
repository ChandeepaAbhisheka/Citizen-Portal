from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import pickle
from typing import List, Dict, Tuple

class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index = None
        self.documents = []
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return np.array(embeddings).astype('float32')
    
    def build_index(self, documents: List[Dict]):
        """Build FAISS index from documents"""
        self.documents = documents
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.create_embeddings(texts)
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
        
        print(f"Index built with {self.index.ntotal} vectors")
    
    def search(self, query: str, k=5) -> List[Tuple[Dict, float]]:
        """Search for similar documents"""
        query_embedding = self.create_embeddings([query])
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distance)))
        
        return results
    
    def save(self, index_path='data/faiss_index.bin', docs_path='data/documents.pkl'):
        """Save index and documents"""
        faiss.write_index(self.index, index_path)
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def load(self, index_path='data/faiss_index.bin', docs_path='data/documents.pkl'):
        """Load index and documents"""
        self.index = faiss.read_index(index_path)
        with open(docs_path, 'rb') as f:
            self.documents = pickle.load(f)

# Build the index
if __name__ == "__main__":
    with open("data/processed_documents.json", "r") as f:
        documents = json.load(f)
    
    store = VectorStore()
    store.build_index(documents)
    store.save()