# from google import genai
# from typing import List, Dict, Optional
# import os
# from sentence_transformers import SentenceTransformer
# from PIL import Image


# class GeminiComplete:
#     """Complete Gemini API implementation using the 2025 SDK"""

#     def __init__(self, api_key: Optional[str] = None):
#         api_key = api_key or os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             raise ValueError("Gemini API key not provided")

#         # Initialize Gemini client (2025)
#         self.client = genai.Client(api_key=api_key)

#         # Model names
#         self.chat_model = "gemini-1.5-pro"
#         self.vision_model = "gemini-1.5-flash"

#         # External embedding model
#         self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

#         print("✓ Gemini (2025) initialized successfully")

#     # -------------------------------------------------------
#     # 1. Embeddings
#     # -------------------------------------------------------
#     def generate_embeddings(self, text: str) -> List[float]:
#         embedding = self.embedding_model.encode(text)
#         return embedding.tolist()

#     # -------------------------------------------------------
#     # 2. RAG Answer Generation
#     # -------------------------------------------------------
#     def generate_answer(self, query: str, context: str) -> Dict:
#         prompt = f"""
# You are a helpful assistant for a citizen services portal in Sri Lanka.

# Answer ONLY using the following context. 
# If information is missing, reply: "I don't have enough information to answer that."

# Context:
# {context}

# Question:
# {query}

# Give answer with source references.
# """

#         try:
#             response = self.client.models.generate_content(
#                 model=self.chat_model,
#                 contents=prompt
#             )

#             return {
#                 "answer": response.text,
#                 "success": True
#             }

#         except Exception as e:
#             return {
#                 "answer": f"Error: {e}",
#                 "success": False
#             }

#     # -------------------------------------------------------
#     # 3. Chat with history
#     # -------------------------------------------------------
#     def chat(self, message: str, history: Optional[List[Dict]] = None):
#         history = history or []

#         formatted_history = ""
#         for h in history:
#             formatted_history += f"{h['role']}: {h['content']}\n"

#         prompt = formatted_history + f"User: {message}"

#         response = self.client.models.generate_content(
#             model=self.chat_model,
#             contents=prompt
#         )

#         history.append({"role": "assistant", "content": response.text})

#         return {
#             "response": response.text,
#             "history": history
#         }

#     # -------------------------------------------------------
#     # 4. Vision Analysis
#     # -------------------------------------------------------
#     def analyze_image(self, image_path: str, prompt: str = "Describe this image") -> str:
#         img = Image.open(image_path)

#         response = self.client.models.generate_content(
#             model=self.vision_model,
#             contents=[prompt, img]
#         )

#         return response.text or ""


#     # -------------------------------------------------------
#     # 5. Summarization
#     # -------------------------------------------------------
#     def summarize_text(self, text: str, max_words: int = 100) -> str:
#         prompt = f"Summarize this in about {max_words} words:\n\n{text}"

#         response = self.client.models.generate_content(
#             model=self.chat_model,
#             contents=prompt
#         )

#         return response.text or ""

#     # -------------------------------------------------------
#     # 6. Keyword Extraction
#     # -------------------------------------------------------
#     def extract_keywords(self, text: str, n_keywords: int = 5) -> List[str]:
#         prompt = f"""
# Extract the top {n_keywords} keywords.
# Return ONLY keywords separated by commas.

# Text:
# {text}
# """

#         response = self.client.models.generate_content(
#             model=self.chat_model,
#             contents=prompt
#         )
#         raw = response.text or "" 

#         return [k.strip() for k in raw.split(",") if k.strip()][:n_keywords]

#     # -------------------------------------------------------
#     # 7. Language Detection
#     # -------------------------------------------------------
#     def detect_language(self, text: str) -> str:
#         prompt = f"What language is this text? Reply with only the language name:\n{text}"

#         response = self.client.models.generate_content(
#             model=self.chat_model,
#             contents=prompt
#         )
#         raw = response.text or ""

#         return raw.strip()

#     # -------------------------------------------------------
#     # 8. Translation
#     # -------------------------------------------------------
#     def translate(self, text: str, target_language: str) -> str:
#         prompt = f"Translate this text to {target_language}:\n{text}"

#         response = self.client.models.generate_content(
#             model=self.chat_model,
#             contents=prompt
#         )

#         return response.text or ""


# # -------------------------------------------------------
# # Example usage
# # -------------------------------------------------------
# if __name__ == "__main__":
#     gemini = GeminiComplete()

#     context = "To apply for a passport, you need: Birth certificate, NIC, 2 photos."
#     query = "What documents do I need for a passport?"

#     result = gemini.generate_answer(query, context)
#     print("Answer:", result["answer"])


# ai/gemini_complete.py

import google.generativeai as genai
import os
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer

class GeminiComplete:
    """Complete Gemini API implementation with better error handling"""
    
    def __init__(self, api_key: Optional[str] = None):
        # 1. Get API key safely
        api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found! Please add it to your .env file")
        
        # 2. Configure Gemini API
        try:
            genai.configure(api_key=api_key)  # type: ignore
            
            # Use the model found in your check_models.py list
            self.model = genai.GenerativeModel('gemini-2.5-flash')  # type: ignore
            print("✅ Gemini API (2.5-Flash) connected!")
            
        except Exception as e:
            print(f"❌ Gemini Connection Error: {e}")
            raise e
        
        # 3. Initialize Embedding Model (REQUIRED for Pinecone)
        print("⏳ Loading embedding model... (this may take a moment)")
        try:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Embeddings model initialized!")
        except Exception as e:
            print(f"❌ Embedding Model Failed: {e}")
            self.embedding_model = None

    # --- RESTORED FUNCTION (Critical for RAG) ---
    def generate_embeddings(self, text: str) -> List[float]:
        """Convert text to numbers for Pinecone search"""
        if not self.embedding_model:
            raise ValueError("Embedding model is not loaded.")
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    # --------------------------------------------
    
    def generate_answer(self, query: str, context: str) -> Dict:
        """Generate answer with a smarter prompt to handle greetings"""
        
        # IMPROVED PROMPT: Handles "Hello" without failing
        prompt = f"""You are a helpful assistant for a citizen services portal in Sri Lanka.

Context information:
{context}

User Question: {query}

Instructions:
1. If the user is greeting you (like "hello", "hi"), reply politely and ask how you can help.
2. If the user asks a specific question, answer it using ONLY the Context information provided above.
3. If the answer is not in the context, say "I don't have that specific information in my database, but I can help with Passports, IDs, and Tax information."
"""
        
        try:
            response = self.model.generate_content(prompt)
            return {'answer': response.text, 'success': True}
        except Exception as e:
            print(f"❌ Generation Error: {e}")
            return {'answer': f"I encountered an error: {str(e)}", 'success': False}
    
    def chat(self, message: str, history: Optional[List[Dict]] = None) -> Dict:
        """Interactive chat with conversation history"""
        try:
            # 1. Prepare history for Gemini
            chat_history = []
            if history:
                for msg in history:
                    role = 'model' if msg.get('role') == 'assistant' else 'user'
                    chat_history.append({'role': role, 'parts': [msg.get('content', '')]})

            # 2. Start Chat
            chat = self.model.start_chat(history=chat_history)
            response = chat.send_message(message)

            # 3. Return result with updated history
            new_history = history or []
            new_history.append({'role': 'user', 'content': message})
            new_history.append({'role': 'assistant', 'content': response.text})

            return {
                'response': response.text,
                'history': new_history,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Chat error: {str(e)}")
            return {
                'response': f"Error: {str(e)}",
                'history': history or [],
                'success': False
            }

# --- TEST BLOCK ---
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing Gemini Complete...")
    
    try:
        gemini = GeminiComplete()
        
        # Test 1: Embeddings
        print("\n1. Testing Embeddings...")
        emb = gemini.generate_embeddings("Hello")
        print(f"✓ Generated {len(emb)} dimensions")
        
        # Test 2: RAG Answer (The Greeting)
        print("\n2. Testing Greeting...")
        result_hello = gemini.generate_answer(
            query="Hello",
            context="To apply for a passport, you need: Birth certificate."
        )
        print(f"✓ Reply to Hello: {result_hello['answer']}")

        # Test 3: RAG Answer (The Fact)
        print("\n3. Testing Facts...")
        result_fact = gemini.generate_answer(
            query="What do I need for a passport?",
            context="To apply for a passport, you need: Birth certificate."
        )
        print(f"✓ Reply to Fact: {result_fact['answer']}")
        
    except Exception as e:
        import traceback
        print(f"\n❌ Test failed: {str(e)}")
        traceback.print_exc()