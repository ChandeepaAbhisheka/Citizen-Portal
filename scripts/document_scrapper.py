import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import io
from typing import List, Dict
from ai.gemini_rag import GeminiRAGSystem
import time

class DocumentScraper:
    """Scrape and index government documents"""
    
    def __init__(self):
        self.rag = GeminiRAGSystem()
    
    def scrape_pdf_from_url(self, url: str) -> str:
        """Download and extract text from PDF URL"""
        try:
            response = requests.get(url, timeout=30)
            pdf_file = io.BytesIO(response.content)
            
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            return text
        except Exception as e:
            print(f"Error scraping PDF {url}: {e}")
            return ""
    
    def scrape_html(self, url: str) -> str:
        """Scrape text from HTML page"""
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            text = soup.get_text(separator='\n')
            
            # Clean up
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join([line for line in lines if line])
            
            return text
        except Exception as e:
            print(f"Error scraping HTML {url}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def scrape_and_index(self, url_list: List[Dict]):
        """
        Scrape documents and add to RAG system
        
        url_list format:
        [
            {"url": "https://example.com/doc.pdf", "type": "pdf", "title": "Document Title"},
            {"url": "https://example.com/page.html", "type": "html", "title": "Page Title"}
        ]
        """
        all_documents = []
        
        for item in url_list:
            url = item['url']
            doc_type = item['type']
            title = item.get('title', url)
            
            print(f"\n📄 Scraping: {title}")
            print(f"   URL: {url}")
            
            # Scrape content
            if doc_type == 'pdf':
                text = self.scrape_pdf_from_url(url)
            else:
                text = self.scrape_html(url)
            
            if not text:
                print(f"   ⚠️  No content extracted")
                continue
            
            # Chunk the text
            chunks = self.chunk_text(text, chunk_size=800, overlap=150)
            print(f"   ✓ Extracted {len(chunks)} chunks")
            
            # Create documents
            for i, chunk in enumerate(chunks):
                all_documents.append({
                    'text': chunk,
                    'source': url,
                    'title': title,
                    'chunk_id': i
                })
            
            # Be nice to servers
            time.sleep(1)
        
        # Index all documents
        if all_documents:
            print(f"\n📚 Indexing {len(all_documents)} document chunks...")
            count = self.rag.add_documents(all_documents)
            print(f"✓ Successfully indexed {count} documents!")
        
        return len(all_documents)

# Example usage
if __name__ == "__main__":
    scraper = DocumentScraper()
    
    # Sri Lankan government services URLs
    urls_to_scrape = [
        {
            "url": "https://www.immigration.gov.lk",
            "type": "html",
            "title": "Immigration and Emigration Department"
        },
        {
            "url": "https://www.ird.gov.lk",
            "type": "html",
            "title": "Inland Revenue Department"
        },
        # Add more URLs here
    ]
    
    # Scrape and index
    total = scraper.scrape_and_index(urls_to_scrape)
    print(f"\n🎉 Done! Indexed {total} total documents")