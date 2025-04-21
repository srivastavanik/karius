import os
from typing import List, Dict, Any, Optional
import pinecone
from langchain.vectorstores.pinecone import Pinecone as LangchainPinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from .novita_adapters import NovitaEmbeddings, NovitaLLM
from .config import settings

# RAG prompt templates
MARKET_EXPANSION_TEMPLATE = """
You are an AI market analyst assistant for Karius, a company specializing in infectious disease diagnostics.
Your task is to analyze the following information and provide strategic insights.

Context information from global health and market data:
{context}

Based only on the above context, answer the following question about market expansion or partner opportunities:
Question: {question}

Provide a structured answer with:
1. Key findings/insights
2. Strategic recommendations
3. Potential risks or limitations
"""

PARTNER_DISCOVERY_TEMPLATE = """
You are an AI partner discovery assistant for Karius, a company specializing in infectious disease diagnostics.
Your task is to identify and evaluate potential partners based on the provided information.

Context information from global health data, hospital directories, and competitor analysis:
{context}

Based only on the above context, answer the following question about potential partners or collaboration opportunities:
Question: {question}

Provide a structured answer with:
1. Evaluation of potential partners
2. Strategic fit with Karius
3. Next steps for engagement
"""

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for Karius market expansion."""
    
    def __init__(self, use_contextual_compression: bool = True):
        """Initialize the RAG pipeline."""
        # Initialize components
        self.embeddings = NovitaEmbeddings()
        self.llm = NovitaLLM(temperature=0.3)  # Lower temperature for more factual responses
        
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.pinecone_api_key,
            environment=settings.pinecone_environment
        )
        
        # Connect to Pinecone index
        if settings.pinecone_index_name not in pinecone.list_indexes():
            raise ValueError(f"Pinecone index '{settings.pinecone_index_name}' does not exist. Please run the embedding script first.")
        
        # Set up the vector store and retriever
        self.vectorstore = LangchainPinecone(
            index=pinecone.Index(settings.pinecone_index_name),
            embedding=self.embeddings.embed_query,
            text_key="content"  # This should match how documents are stored in Pinecone
        )
        
        # Base retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}  # Retrieve top 10 documents
        )
        
        # Optionally use contextual compression to extract the most relevant parts
        if use_contextual_compression:
            compressor = LLMChainExtractor.from_llm(self.llm)
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=self.retriever
            )
        
        # Create default QA chain
        self.default_qa = self._create_qa_chain(MARKET_EXPANSION_TEMPLATE)
        
        # Additional specialized QA chains
        self.partner_qa = self._create_qa_chain(PARTNER_DISCOVERY_TEMPLATE)
    
    def _create_qa_chain(self, template_str: str):
        """Create a QA chain with the specified prompt template."""
        prompt = PromptTemplate(
            template=template_str,
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Simple context concatenation
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True  # Include source docs in response
        )
    
    def query(self, question: str, query_type: str = "market") -> Dict[str, Any]:
        """
        Run a query through the appropriate RAG pipeline.
        
        Args:
            question: User's question
            query_type: Type of query - "market" or "partner"
        
        Returns:
            Dict with response and source documents
        """
        if query_type.lower() == "partner":
            result = self.partner_qa({"query": question})
        else:
            result = self.default_qa({"query": question})
        
        return {
            "answer": result["result"],
            "source_documents": result["source_documents"]
        }
    
    def filter_by_metadata(self, metadata_filters: Dict[str, Any]):
        """
        Apply metadata filters to the retriever.
        
        Args:
            metadata_filters: Dict of metadata field:value to filter on
        """
        # Update the retriever with metadata filters
        filtered_retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 10,
                "filter": metadata_filters
            }
        )
        
        # Update the current retriever
        self.retriever = filtered_retriever
        
        # Recreate QA chains with the new retriever
        self.default_qa = self._create_qa_chain(MARKET_EXPANSION_TEMPLATE)
        self.partner_qa = self._create_qa_chain(PARTNER_DISCOVERY_TEMPLATE) 