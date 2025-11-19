from google import genai
from typing import List, Dict, Optional
import os
from sentence_transformers import SentenceTransformer
from PIL import Image


class GeminiComplete:
    """Complete Gemini API implementation using the 2025 SDK"""

    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not provided")

        # Initialize Gemini client (2025)
        self.client = genai.Client(api_key=api_key)

        # Model names
        self.chat_model = "gemini-1.5-pro"
        self.vision_model = "gemini-1.5-flash"

        # External embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        print("✓ Gemini (2025) initialized successfully")

    # -------------------------------------------------------
    # 1. Embeddings
    # -------------------------------------------------------
    def generate_embeddings(self, text: str) -> List[float]:
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    # -------------------------------------------------------
    # 2. RAG Answer Generation
    # -------------------------------------------------------
    def generate_answer(self, query: str, context: str) -> Dict:
        prompt = f"""
You are a helpful assistant for a citizen services portal in Sri Lanka.

Answer ONLY using the following context. 
If information is missing, reply: "I don't have enough information to answer that."

Context:
{context}

Question:
{query}

Give answer with source references.
"""

        try:
            response = self.client.models.generate_content(
                model=self.chat_model,
                contents=prompt
            )

            return {
                "answer": response.text,
                "success": True
            }

        except Exception as e:
            return {
                "answer": f"Error: {e}",
                "success": False
            }

    # -------------------------------------------------------
    # 3. Chat with history
    # -------------------------------------------------------
    def chat(self, message: str, history: Optional[List[Dict]] = None):
        history = history or []

        formatted_history = ""
        for h in history:
            formatted_history += f"{h['role']}: {h['content']}\n"

        prompt = formatted_history + f"User: {message}"

        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt
        )

        history.append({"role": "assistant", "content": response.text})

        return {
            "response": response.text,
            "history": history
        }

    # -------------------------------------------------------
    # 4. Vision Analysis
    # -------------------------------------------------------
    def analyze_image(self, image_path: str, prompt: str = "Describe this image") -> str:
        img = Image.open(image_path)

        response = self.client.models.generate_content(
            model=self.vision_model,
            contents=[prompt, img]
        )

        return response.text or ""


    # -------------------------------------------------------
    # 5. Summarization
    # -------------------------------------------------------
    def summarize_text(self, text: str, max_words: int = 100) -> str:
        prompt = f"Summarize this in about {max_words} words:\n\n{text}"

        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt
        )

        return response.text or ""

    # -------------------------------------------------------
    # 6. Keyword Extraction
    # -------------------------------------------------------
    def extract_keywords(self, text: str, n_keywords: int = 5) -> List[str]:
        prompt = f"""
Extract the top {n_keywords} keywords.
Return ONLY keywords separated by commas.

Text:
{text}
"""

        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt
        )
        raw = response.text or "" 

        return [k.strip() for k in raw.split(",") if k.strip()][:n_keywords]

    # -------------------------------------------------------
    # 7. Language Detection
    # -------------------------------------------------------
    def detect_language(self, text: str) -> str:
        prompt = f"What language is this text? Reply with only the language name:\n{text}"

        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt
        )
        raw = response.text or ""

        return raw.strip()

    # -------------------------------------------------------
    # 8. Translation
    # -------------------------------------------------------
    def translate(self, text: str, target_language: str) -> str:
        prompt = f"Translate this text to {target_language}:\n{text}"

        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt
        )

        return response.text or ""


# -------------------------------------------------------
# Example usage
# -------------------------------------------------------
if __name__ == "__main__":
    gemini = GeminiComplete()

    context = "To apply for a passport, you need: Birth certificate, NIC, 2 photos."
    query = "What documents do I need for a passport?"

    result = gemini.generate_answer(query, context)
    print("Answer:", result["answer"])
