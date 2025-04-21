import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .models import get_db, DataRecord
from .rag_pipeline import RAGPipeline
from .config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Karius Market Expansion AI",
    description="AI-Driven Market Expansion & Partner Discovery tool for Karius",
    version="1.0",
)

# Add CORS middleware to allow cross-origin requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Pipeline as a global variable (lazily loaded on first request)
_rag_pipeline: Optional[RAGPipeline] = None

def get_rag_pipeline() -> RAGPipeline:
    """Create or return the RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        try:
            _rag_pipeline = RAGPipeline()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize RAG pipeline: {str(e)}")
    return _rag_pipeline

# --- Request/Response Models ---

class QueryRequest(BaseModel):
    """Request model for querying the AI assistant."""
    question: str
    query_type: str = "market"  # 'market' or 'partner'
    metadata_filters: Optional[Dict[str, Any]] = None

class SourceDocument(BaseModel):
    """Model for source documents returned with answers."""
    content: str
    source: str
    metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    """Response model for AI assistant answers."""
    answer: str
    sources: List[SourceDocument]

class MetadataFilterOption(BaseModel):
    """Model for available metadata filter options."""
    field: str
    values: List[str]

class StatsResponse(BaseModel):
    """Response model for database statistics."""
    total_records: int
    by_source: Dict[str, int]

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Root endpoint with API info."""
    return {
        "message": "Karius Market Expansion AI API",
        "version": "1.0",
        "docs_url": "/docs"
    }

@app.post("/query", response_model=QueryResponse)
def query_assistant(
    request: QueryRequest,
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    """Submit a question to the AI assistant and get an answer."""
    try:
        # Apply metadata filters if provided
        if request.metadata_filters:
            rag.filter_by_metadata(request.metadata_filters)
        
        # Process the query
        result = rag.query(request.question, request.query_type)
        
        # Format source documents
        sources = []
        for doc in result.get("source_documents", []):
            source_doc = SourceDocument(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                metadata=doc.metadata
            )
            sources.append(source_doc)
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """Get statistics about the ingested data."""
    try:
        # Get total count
        total_records = db.query(DataRecord).count()
        
        # Get counts by source
        by_source = {}
        source_counts = db.query(DataRecord.source, db.func.count(DataRecord.id)).group_by(DataRecord.source).all()
        for source, count in source_counts:
            by_source[source] = count
        
        return StatsResponse(
            total_records=total_records,
            by_source=by_source
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/filters", response_model=List[MetadataFilterOption])
def get_filter_options(db: Session = Depends(get_db)):
    """Get available metadata filters based on the ingested data."""
    try:
        # This is a simplified example - in a real implementation, you'd need to
        # inspect the actual metadata in your database to extract available filters
        # This might require custom SQL queries depending on how metadata is stored
        
        # Example of hardcoded response for now
        return [
            MetadataFilterOption(field="country", values=["USA", "UK", "Germany", "Japan", "Brazil"]),
            MetadataFilterOption(field="year", values=["2018", "2019", "2020", "2021", "2022"]),
            MetadataFilterOption(field="source", values=["who_csv", "cdc_api", "pubmed_api", "purchased", "web_scrape"]),
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving filter options: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # For direct script execution - typically you'd use 'uvicorn app.main:app --reload'
    uvicorn.run(app, host="0.0.0.0", port=8000) 