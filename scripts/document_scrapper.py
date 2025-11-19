import os
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import re
from typing import List, Dict
import json

class DocumentScraper:
    def __init__(self, output_dir="data/scraped_docs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def scrape_pdf(self, url: str, filename: str) -> str:
        """Download and extract text from PDF"""
        response = requests.get(url, timeout=30)
        pdf_path = os.path.join(self.output_dir, filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return self.clean_text(text)
    
    def scrape_html(self, url: str) -> str:
        """Scrape and extract text from HTML page"""
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text = soup.get_text()
        return self.clean_text(text)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size=500, overlap=50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks

# Example usage
if __name__ == "__main__":
    scraper = DocumentScraper()
    
    # List of government document URLs
    urls = [
        {"url": "https://example.gov/services/passport.pdf", "type": "pdf"},
        {"url": "https://example.gov/services/tax-filing.html", "type": "html"},
    ]
    
    all_documents = []
    
    for doc in urls:
        if doc["type"] == "pdf":
            text = scraper.scrape_pdf(doc["url"], f"doc_{len(all_documents)}.pdf")
        else:
            text = scraper.scrape_html(doc["url"])
        
        chunks = scraper.chunk_text(text)
        all_documents.extend([
            {"text": chunk, "source": doc["url"], "chunk_id": i}
            for i, chunk in enumerate(chunks)
        ])
    
    # Save processed documents
    with open("data/processed_documents.json", "w") as f:
        json.dump(all_documents, f, indent=2)