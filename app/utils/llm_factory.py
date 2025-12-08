from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.config.settings import Settings
import os

class LLMFactory:
    """
    Factory to create Chat Model instances (Gemini, OpenAI, Claude).
    Centralizes API key management and configuration.
    """
    
    @staticmethod
    def create_chat_model(provider: str = "gemini", temperature: float = 0.7) -> BaseChatModel:
        settings = Settings()
        
        if provider == "gemini":
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
                
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=api_key,
                temperature=temperature,
                convert_system_message_to_human=True 
            )
            
        # Placeholders for future extensibility
        elif provider == "openai":
            raise NotImplementedError("OpenAI support not yet implemented")
        elif provider == "claude":
            raise NotImplementedError("Claude support not yet implemented")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    @staticmethod
    def create_embeddings_model(provider: str = "gemini"):
        settings = Settings()
        
        if provider == "gemini":
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
                
            return GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=api_key,
                task_type="retrieval_document"
            )
        else:
            raise NotImplementedError(f"Embeddings provider {provider} not supported user")
