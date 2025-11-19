from ai.gemini_complete import GeminiComplete
from ai.chroma_store import ChromaVectorStore
from typing import Dict, List, Optional
import json

class GeminiRAGSystem:
    """Complete RAG system using Gemini + ChromaDB (100% FREE)"""
    
    def __init__(self):
        print("🚀 Initializing Gemini RAG System...")
        self.gemini = GeminiComplete()
        self.vector_store = ChromaVectorStore()
        print("✓ System ready!")
    
    def add_documents(self, documents: List[Dict]) -> int:
        """Add documents to knowledge base"""
        return self.vector_store.add_documents(documents)
    
    def search_only(self, query: str, n_results: int = 5) -> List[Dict]:
        """Just search without answer generation"""
        return self.vector_store.search(query, n_results)
    
    def answer_query(self, query: str, n_results: int = 5) -> Dict:
        """
        Complete RAG pipeline:
        1. Retrieve relevant documents
        2. Generate answer with Gemini
        3. Return answer with sources
        """
        
        # Step 1: Retrieve relevant documents
        docs = self.vector_store.search(query, n_results)
        
        if not docs:
            return {
                'query': query,
                'answer': "I don't have information about that in my knowledge base. Please try rephrasing your question or contact support.",
                'sources': [],
                'confidence': 'low',
                'retrieved_docs': 0
            }
        
        # Step 2: Prepare context with sources
        context = "\n\n".join([
            f"[Source {i+1}: {doc['source']}]\n{doc['text']}"
            for i, doc in enumerate(docs)
        ])
        
        # Step 3: Generate answer with Gemini
        result = self.gemini.generate_answer(query, context)
        
        if not result['success']:
            return {
                'query': query,
                'answer': "I encountered an error generating the answer. Please try again.",
                'sources': [],
                'confidence': 'low',
                'error': result.get('error', 'Unknown error')
            }
        
        # Step 4: Format response
        return {
            'query': query,
            'answer': result['answer'],
            'sources': [
                {
                    'url': doc['source'],
                    'title': doc.get('title', 'Document'),
                    'relevance_score': doc['score']
                }
                for doc in docs
            ],
            'confidence': 'high' if len(docs) >= 3 else 'medium',
            'retrieved_docs': len(docs),
            'model': 'gemini-pro'
        }
    
    def chat(self, message: str, history: Optional[List[Dict]] = None) -> Dict:
        """Chat with conversation history"""
        return self.gemini.chat(message, history)
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return self.vector_store.get_stats()

# Example usage and testing
if __name__ == "__main__":
    # Initialize RAG system
    rag = GeminiRAGSystem()
    
    # Add sample documents
    print("\n📚 Adding documents...")
    docs = [
        {
            'text': '''Passport Application Process in Sri Lanka:
            
            To apply for a Sri Lankan passport, follow these steps:
            1. Visit the Department of Immigration and Emigration office
            2. Required documents:
               - Birth certificate (original and certified copy)
               - National Identity Card (NIC)
               - Two recent passport-sized photographs (white background)
               - Previous passport (if renewing)
            
            Fees:
            - Standard passport: Rs. 3,000
            - Express service: Rs. 6,000
            
            Processing time:
            - Standard: 7-10 working days
            - Express: 3-5 working days''',
            'source': 'https://immigration.gov.lk/passport-application',
            'title': 'Passport Application Guide',
            'chunk_id': 0
        },
        {
            'text': '''Tax Filing in Sri Lanka:
            
            Individual taxpayers must file their tax returns annually.
            
            Key deadlines:
            - Individual tax returns: November 30th
            - Corporate tax returns: December 31st
            
            Required documents:
            - Income statements
            - Bank statements
            - Investment details
            - Previous year's tax returns
            
            You can file online at www.ird.gov.lk or visit your nearest Inland Revenue office.''',
            'source': 'https://ird.gov.lk/tax-filing-guide',
            'title': 'Tax Filing Information',
            'chunk_id': 0
        },
        {
            'text': '''National Identity Card (NIC) Application:
            
            Sri Lankan citizens must obtain a National Identity Card at age 16.
            
            Application process:
            1. Visit your Divisional Secretariat office
            2. Bring birth certificate and proof of residence
            3. Fill out Form A (available at the office)
            4. Provide fingerprints and photo
            
            Processing time: 2-4 weeks
            Fee: Free of charge
            
            For replacements or corrections, visit the same office with supporting documents.''',
            'source': 'https://www.ps.gov.lk/nic-application',
            'title': 'NIC Application Guide',
            'chunk_id': 0
        }
    ]
    
    rag.add_documents(docs)
    
    # Test queries
    print("\n" + "="*60)
    print("🤖 Testing RAG System")
    print("="*60)
    
    test_queries = [
        "What documents do I need to apply for a passport?",
        "How much does an express passport cost?",
        "When is the tax filing deadline?",
        "How do I get a National ID card?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 60)
        
        result = rag.answer_query(query)
        
        print(f"💡 Answer:\n{result['answer']}\n")
        print(f"📊 Confidence: {result['confidence']}")
        print(f"📚 Sources: {len(result['sources'])} documents")
        
        if result['sources']:
            print("\n🔗 References:")
            for i, source in enumerate(result['sources'], 1):
                print(f"  {i}. {source['title']} - Relevance: {source['relevance_score']:.2f}")
                print(f"     {source['url']}")
    
    # Display stats
    print("\n" + "="*60)
    stats = rag.get_stats()
    print(f"📈 System Stats: {stats['total_documents']} documents in knowledge base")
    print("="*60)
