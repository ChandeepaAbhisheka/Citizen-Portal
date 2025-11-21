"""
Gemini AI Handler for Citizen Portal
"""

import google.generativeai as genai  # type: ignore
import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    """Gemini AI class for generating responses"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini AI"""
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not found! Add it to .env file")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)  # type: ignore
        
        # Initialize the model (FREE!)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # type: ignore
        
        print("✅ Gemini AI initialized!")
    
    def generate_response(self, query: str, context: str = "") -> Dict[str, Any]:
        """Generate response to user query"""
        
        try:
            if context:
                prompt = f"""You are a helpful assistant for a Citizen Services Portal in Sri Lanka.

Answer the user's question based on this context. Be helpful and concise.
If the answer is not in the context, say so politely.

CONTEXT:
{context}

USER'S QUESTION: {query}

Answer:"""
            else:
                prompt = f"""You are a helpful assistant for a Citizen Services Portal in Sri Lanka.

Answer this question helpfully: {query}

Answer:"""
            
            response = self.model.generate_content(prompt)  # type: ignore
            
            return {
                "success": True,
                "answer": response.text,
                "model": "gemini-1.5-flash"
            }
        
        except Exception as e:
            print(f"❌ Gemini Error: {str(e)}")
            return {
                "success": False,
                "answer": "Sorry, I encountered an error. Please try again.",
                "error": str(e)
            }
    
    def chat(self, message: str, history: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Chat with history"""
        
        try:
            chat = self.model.start_chat(history=history if history is not None else [])  # type: ignore
            response = chat.send_message(message)  # type: ignore
            
            return {
                "success": True,
                "response": response.text,
                "history": chat.history
            }
        except Exception as e:
            return {
                "success": False,
                "response": "Sorry, error occurred.",
                "error": str(e)
            }


# Test if run directly
if __name__ == "__main__":
    print("🧪 Testing Gemini AI...")
    
    ai = GeminiAI()
    
    result = ai.generate_response("How do I get a passport in Sri Lanka?")
    
    if result["success"]:
        print(f"✅ Answer: {result['answer'][:200]}...")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")