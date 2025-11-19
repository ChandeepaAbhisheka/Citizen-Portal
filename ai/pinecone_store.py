from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class PineconeStore:
    def __init__(self, api_key: str, index_name: str):
        """Initialize Pinecone client and connect to / create index."""
        
        self.pc = Pinecone(api_key=api_key)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_name = index_name

        # Check existing indexes
        existing_indexes = self.pc.list_indexes().names()

        if index_name not in existing_indexes:
            print(f"[INFO] Creating index '{index_name}'...")

            self.pc.create_index(
                name=index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        # Connect to Pinecone index
        self.index = self.pc.Index(index_name)
        print(f"[INFO] Connected to index '{index_name}'.")

    def upsert_documents(self, documents: List[Dict]):
        """Embed and upload documents to Pinecone."""
        
        texts = [doc["text"] for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        vectors = [
            (
                f"doc_{i}",
                embedding.tolist(),
                {"text": doc["text"], "source": doc["source"]}
            )
            for i, (embedding, doc) in enumerate(zip(embeddings, documents))
        ]

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

        print(f"[INFO] Upserted {len(documents)} documents.")

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search Pinecone index with a text query."""
        
        query_embedding = self.model.encode([query])[0]

        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=k,
            include_metadata=True
        )

        # Access matches - cast to dict if needed to avoid type warnings
        matches = getattr(results, 'matches', [])
        
        return [
            {
                "text": match.metadata.get("text"),
                "source": match.metadata.get("source"),
                "score": match.score
            }
            for match in matches
        ]