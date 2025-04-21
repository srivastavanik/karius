import sys
import os
import time
import argparse
from typing import List, Dict, Any, Tuple, Optional
from tqdm import tqdm
import pinecone
from novita_sdk import EmbeddingClient
from sqlalchemy import select, and_

# Add project root to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.models import SessionLocal, DataRecord
from app.config import settings

def get_db_session():
    """Provides a database session."""
    return SessionLocal()

def initialize_pinecone():
    """Initialize the Pinecone client and ensure the index exists."""
    print(f"Initializing Pinecone (environment: {settings.pinecone_environment})")
    
    # Initialize Pinecone client
    pinecone.init(
        api_key=settings.pinecone_api_key,
        environment=settings.pinecone_environment
    )
    
    # Check if our index already exists
    if settings.pinecone_index_name not in pinecone.list_indexes():
        print(f"Creating new Pinecone index: {settings.pinecone_index_name}")
        pinecone.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.pinecone_embedding_dimension,
            metric="cosine"
        )
        # Wait for index to be ready
        time.sleep(1)
    
    # Connect to the index
    index = pinecone.Index(settings.pinecone_index_name)
    print(f"Connected to Pinecone index: {settings.pinecone_index_name}")
    
    return index

def initialize_embedding_client():
    """Initialize the Novita embedding client."""
    print("Initializing Novita embedding client")
    embedding_client = EmbeddingClient(api_key=settings.novita_api_key)
    return embedding_client

def get_records_to_embed(db_session, source=None, limit=None, skip_existing=False, batch_size=100):
    """
    Retrieve records from the database that need embedding.
    
    Args:
        db_session: SQLAlchemy database session
        source: Optional filter by source type
        limit: Optional maximum number of records to process
        skip_existing: Whether to skip records that might have already been embedded (requires implementation)
        batch_size: Number of records to retrieve in each batch
    
    Yields:
        Batches of records to be processed
    """
    # Base query
    query = select(DataRecord)
    
    # Add source filter if specified
    if source:
        query = query.where(DataRecord.source == source)
    
    # TODO: If skip_existing is True, implement a way to track which records have already been embedded
    # This might require adding a new field to the DataRecord model or maintaining a separate table
    
    # Execute query with limit if specified
    if limit:
        query = query.limit(limit)
    
    # Fetch records in batches for memory efficiency
    offset = 0
    while True:
        batch_query = query.offset(offset).limit(batch_size)
        batch_records = list(db_session.execute(batch_query).scalars().all())
        
        if not batch_records:
            break
            
        yield batch_records
        
        offset += len(batch_records)
        if limit and offset >= limit:
            break

def prepare_metadata(record: DataRecord) -> Dict[str, Any]:
    """
    Prepare metadata for storage in Pinecone.
    
    Args:
        record: A DataRecord instance
    
    Returns:
        A dict of metadata suitable for Pinecone
    """
    # Start with base metadata: record ID and source
    metadata = {
        "record_id": record.id,
        "source": record.source,
    }
    
    # Add important metadata fields from the record's metadata
    # Select only fields that you want to be searchable/filterable in Pinecone
    if record.metadata:
        # Example: Extract common fields like region, date, type
        # Adjust based on your actual metadata structure
        for key in ["region", "country", "year", "type", "category"]:
            if key in record.metadata and record.metadata[key] is not None:
                metadata[key] = record.metadata[key]
    
    return metadata

def embed_and_store_records(records: List[DataRecord], embedding_client, pinecone_index):
    """
    Generate embeddings for records and store them in Pinecone.
    
    Args:
        records: List of DataRecord objects
        embedding_client: Initialized Novita embedding client
        pinecone_index: Initialized Pinecone index
    
    Returns:
        Tuple of (success_count, error_count)
    """
    success_count = 0
    error_count = 0
    
    # Prepare data for batch embedding
    record_ids = []
    contents = []
    
    for record in records:
        record_ids.append(record.id)
        contents.append(record.content)
    
    # Skip if no valid records
    if not contents:
        return 0, 0
    
    try:
        # Generate embeddings in batch
        print(f"Generating embeddings for {len(contents)} records using model: {settings.novita_embedding_model}")
        embeddings = embedding_client.embed_batch(
            model=settings.novita_embedding_model,
            input=contents
        )
        
        # Prepare records for Pinecone
        pinecone_records = []
        for i, (record_id, embedding, record) in enumerate(zip(record_ids, embeddings, records)):
            metadata = prepare_metadata(record)
            pinecone_records.append((str(record_id), embedding, metadata))
        
        # Upsert to Pinecone
        print(f"Upserting {len(pinecone_records)} vectors to Pinecone")
        pinecone_index.upsert(vectors=pinecone_records)
        
        success_count = len(pinecone_records)
        
    except Exception as e:
        print(f"Error in batch embedding/upsert: {e}")
        # If batch fails, try embedding one by one to identify problematic records
        for record in records:
            try:
                # Generate embedding
                embedding = embedding_client.embed(
                    model=settings.novita_embedding_model,
                    input=record.content
                )
                
                # Prepare metadata
                metadata = prepare_metadata(record)
                
                # Upsert to Pinecone
                pinecone_index.upsert(vectors=[(str(record.id), embedding, metadata)])
                
                success_count += 1
                
            except Exception as e:
                print(f"Error embedding record {record.id}: {e}")
                error_count += 1
    
    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description="Embed records and store them in the vector database.")
    parser.add_argument("--source", help="Filter records by source (e.g., 'who_csv', 'cdc_api').")
    parser.add_argument("--limit", type=int, help="Maximum number of records to process.")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of records to process in each batch.")
    parser.add_argument("--skip-existing", action="store_true", help="Skip records that have already been embedded.")
    
    args = parser.parse_args()
    
    # Initialize database session
    db = get_db_session()
    
    try:
        # Initialize Pinecone
        pinecone_index = initialize_pinecone()
        
        # Initialize Novita embedding client
        embedding_client = initialize_embedding_client()
        
        # Process records in batches
        total_success = 0
        total_errors = 0
        
        print("Starting embedding process...")
        for batch in tqdm(get_records_to_embed(db, args.source, args.limit, args.skip_existing, args.batch_size)):
            success, errors = embed_and_store_records(batch, embedding_client, pinecone_index)
            total_success += success
            total_errors += errors
        
        print(f"Embedding process complete. Successfully embedded: {total_success}, Errors: {total_errors}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    main() 