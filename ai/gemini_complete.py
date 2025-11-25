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
from typing import List, Dict, Optional, Any, cast

class GeminiComplete:
    """Complete Gemini API implementation with better error handling"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Get API key
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "❌ GEMINI_API_KEY not found!\n"
                "Please add it to your .env file"
            )
        
        # Configure Gemini (SDK may differ across versions)
        if hasattr(genai, 'configure'):
            genai.configure(api_key=api_key)  # type: ignore

        # Initialize model (use cast/ignore to satisfy static checkers)
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # type: ignore
        except Exception:
            # Fallback: keep a reference to genai in case the API differs
            self.model = cast(Any, genai)
        
        print("✅ Gemini API initialized successfully!")
    
    def generate_answer(self, query: str, context: str) -> Dict:
        """Generate answer with citations using Gemini"""
        
        prompt = f"""You are a helpful assistant for a citizen services portal in Sri Lanka.
Answer the following question based ONLY on the provided context.
If the answer cannot be found in the context, say "I don't have enough information to answer that specifically, but I can help you with general guidance."
Be concise, clear, and helpful.

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            # Generate content
            response = self.model.generate_content(  # type: ignore
                prompt,
                generation_config=cast(Any, {
                    'temperature': 0.3,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 500,
                })
            )
            
            # IMPORTANT: Check if response has text
            if not response or not response.text:
                return {
                    'answer': "I couldn't generate an answer. Please try rephrasing your question.",
                    'success': False,
                    'error': 'Empty response from Gemini'
                }
            
            return {
                'answer': response.text,
                'success': True,
                'model': 'gemini-1.5-flash'
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini error: {error_msg}")
            
            # Return more helpful error
            return {
                'answer': f"I encountered an error: {error_msg}. Please try again or contact support.",
                'success': False,
                'error': error_msg
            }
    
    def chat(self, message: str, history: Optional[List[Dict]] = None) -> Dict:
        """Interactive chat with conversation history"""
        try:
            chat = self.model.start_chat(history=[])  # type: ignore

            if history:
                for msg in history:
                    role = 'model' if msg.get('role') == 'assistant' else 'user'
                    # cast to Any to avoid strict type checks from the SDK wrapper
                    chat.history.append(cast(Any, {
                        'role': role,
                        'parts': [msg.get('content', '')]
                    }))

            response = chat.send_message(message)  # type: ignore

            # Build a safe history list using getattr to avoid static type errors
            history_out: List[Dict[str, str]] = []
            for h in getattr(chat, 'history', []):
                role = getattr(h, 'role', '')
                parts = getattr(h, 'parts', []) or []
                # parts may contain objects or strings depending on SDK
                content = ''
                try:
                    first = parts[0]
                    # Try multiple ways to extract text
                    content = getattr(first, 'text', first) or ''
                except Exception:
                    content = ''

                history_out.append({'role': role, 'content': content})

            return {
                'response': getattr(response, 'text', str(response)),
                'history': history_out,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Chat error: {str(e)}")
            return {
                'response': f"Error: {str(e)}",
                'history': history or [],
                'success': False
            }


# Test the module
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing Gemini Complete...")
    
    try:
        gemini = GeminiComplete()
        
        # Test with simple context
        result = gemini.generate_answer(
            query="What do I need for a passport?",
            context="To apply for a passport, you need: Birth certificate, National ID, and two photos."
        )
        
        print(f"\n📝 Test Result:")
        print(f"Success: {result['success']}")
        print(f"Answer: {result['answer']}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")