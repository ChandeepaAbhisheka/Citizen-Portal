import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os

class ChromaVectorStore:
    """Free vector database using ChromaDB (no API key needed)"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="citizen_portal_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Free embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"✓ ChromaDB initialized at {persist_directory}")
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to vector store"""
        
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            texts.append(doc['text'])
            metadatas.append({
                'source': doc.get('source', ''),
                'chunk_id': str(doc.get('chunk_id', 0)),
                'title': doc.get('title', '')
            })
            ids.append(f"doc_{i}_{hash(doc['text']) % 10000}")
        
        # Add to ChromaDB
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✓ Added {len(documents)} documents")
        return len(documents)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        
        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        docs = []

        # Ensure results exist and have expected keys
        if not results:
            return docs

        documents = results.get('documents')
        metadatas = results.get('metadatas')
        distances = results.get('distances')

        # Ensure the lists are valid and non-empty
        if not documents or not documents[0]:
            return docs

        if not metadatas or not metadatas[0]:
            metadatas = [[]]  # fallback

        if not distances or not distances[0]:
            distances = [[None] * len(documents[0])]

        for i in range(len(documents[0])):
            doc_text = documents[0][i]

            meta = metadatas[0][i] if i < len(metadatas[0]) else {}
            distance = distances[0][i] if i < len(distances[0]) else None

            docs.append({
                'text': doc_text,
                'source': meta.get('source', ''),
                'title': meta.get('title', ''),
                'score': 1 - distance if distance is not None else None,
                'distance': distance
            })

        return docs

    
    def delete_all(self):
        """Clear all documents"""
        self.client.delete_collection("citizen_portal_docs")
        self.collection = self.client.create_collection("citizen_portal_docs")
    
    def get_stats(self) -> Dict:
        """Get collection stats"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection.name
        }

# Example usage
if __name__ == "__main__":
    store = ChromaVectorStore()
    
    # Test documents
    test_docs = [
        {
            'text': 'How to apply for a passport in Sri Lanka: Visit the Department of Immigration and Emigration. Required documents: Birth certificate, National ID, two passport-sized photos.',
            'source': 'https://immigration.gov.lk/passport',
            'title': 'Passport Application Guide',
            'chunk_id': 0
        },
        {
            'text': 'Tax filing deadlines in Sri Lanka: Individual tax returns must be filed by November 30th. Corporate taxes are due by December 31st.',
            'source': 'https://ird.gov.lk/tax-filing',
            'title': 'Tax Filing Information',
            'chunk_id': 0
        }
    ]
    
    store.add_documents(test_docs)
    
    # Test search
    results = store.search("passport documents needed", n_results=2)
    for doc in results:
        print(f"\nScore: {doc['score']:.2f}")
        print(f"Text: {doc['text'][:100]}...")