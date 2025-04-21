import os
from typing import List, Dict, Any, Mapping, Optional
from novita_sdk import EmbeddingClient, CompletionClient, ChatOptions, ChatMessage, Role

from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.pydantic_v1 import Field, BaseModel

from .config import settings

class NovitaEmbeddings(Embeddings):
    """LangChain adapter for Novita embeddings."""
    
    client: Optional[EmbeddingClient] = None
    model: str = settings.novita_embedding_model
    api_key: str = settings.novita_api_key
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the Novita embeddings with optional API key and model override."""
        self.api_key = api_key or self.api_key
        self.model = model or self.model
        self.client = EmbeddingClient(api_key=self.api_key)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using the Novita API."""
        if not texts:
            return []
        
        embeddings = self.client.embed_batch(
            model=self.model,
            input=texts
        )
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query using the Novita API."""
        embedding = self.client.embed(
            model=self.model,
            input=text
        )
        return embedding

class NovitaLLM(LLM):
    """LangChain adapter for Novita LLM."""
    
    client: Optional[CompletionClient] = None
    model: str = settings.novita_llm_model
    api_key: str = settings.novita_api_key
    temperature: float = 0.7
    max_tokens: int = 1024
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Initialize the Novita LLM with optional parameter overrides."""
        super().__init__()
        self.api_key = api_key or self.api_key
        self.model = model or self.model
        self.temperature = temperature if temperature is not None else self.temperature
        self.max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        self.client = CompletionClient(api_key=self.api_key)
    
    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "novita"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Novita API and return the generated text."""
        # Use Chat API from Novita
        messages = [ChatMessage(role=Role.USER, content=prompt)]
        
        # Set up options
        options = ChatOptions(
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop
        )
        
        # Make the API call
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options=options
        )
        
        return response.message.content

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Return identifying parameters for logging."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        } 