import sys
import os
import argparse
import pandas as pd
from sqlalchemy.orm import Session
import json

# Add project root to the Python path to allow importing from 'app'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.models import SessionLocal, DataRecord
from app.config import settings

def get_db_session():
    """Provides a database session."""
    return SessionLocal()

def ingest_who_csv(db: Session, file_path: str):
    """Ingests data from a WHO CSV file into the database."""
    print(f"Ingesting WHO data from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        added_count = 0
        skipped_count = 0

        # --- Data Processing Logic (Example - needs refinement based on actual CSV structure) ---
        # This is a basic example. You'll need to adapt it based on the specific columns
        # in your WHO CSV files. Decide what constitutes 'content' vs 'metadata'.
        for index, row in df.iterrows():
            try:
                # Example: Concatenate relevant text fields for content
                # Adjust column names based on your actual CSV data
                content_parts = [] 
                if 'IndicatorName' in row and pd.notna(row['IndicatorName']): content_parts.append(f"Indicator: {row['IndicatorName']}")
                if 'Location' in row and pd.notna(row['Location']): content_parts.append(f"Location: {row['Location']}")
                if 'Period' in row and pd.notna(row['Period']): content_parts.append(f"Period: {row['Period']}")
                if 'Dim1' in row and pd.notna(row['Dim1']): content_parts.append(f"Dimension 1: {row['Dim1']}") # Example dimension
                if 'Value' in row and pd.notna(row['Value']): content_parts.append(f"Value: {row['Value']}")

                content = "; ".join(content_parts)
                
                # Store the entire row (converted to dict) as metadata, excluding potentially large/redundant fields
                metadata_dict = row.to_dict()
                # Clean up metadata (e.g., handle NaN values for JSON serialization)
                metadata_cleaned = {k: v if pd.notna(v) else None for k, v in metadata_dict.items()}

                if not content:
                    print(f"Skipping row {index+2}: No content generated.")
                    skipped_count += 1
                    continue

                record = DataRecord(
                    source='who_csv',
                    content=content,
                    metadata=metadata_cleaned
                )
                db.add(record)
                added_count += 1

                # Commit periodically to avoid large transactions
                if added_count % 100 == 0:
                    db.commit()
                    print(f"Committed {added_count} records...")

            except Exception as row_error:
                db.rollback() # Rollback the specific problematic row
                print(f"Error processing row {index + 2}: {row_error}")
                skipped_count += 1
                continue # Continue with the next row

        db.commit() # Commit any remaining records
        print(f"Finished ingesting WHO data. Added: {added_count}, Skipped: {skipped_count}")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        db.rollback() # Rollback the transaction on general error
        print(f"An error occurred during WHO CSV ingestion: {e}")

def ingest_cdc_api(db: Session, api_endpoint: str):
    """Placeholder for ingesting data from the CDC API."""
    print(f"Placeholder: Ingesting CDC data from API: {api_endpoint}")
    # Implementation using requests or Socrata SDK would go here
    # Fetch data, parse JSON/CSV, create DataRecord objects, add to db
    pass

def ingest_pubmed_api(db: Session, query: str):
    """Placeholder for ingesting data from the PubMed API."""
    print(f"Placeholder: Ingesting PubMed data for query: {query}")
    # Implementation using requests to fetch BioC XML/JSON would go here
    # Parse the data, extract relevant text/metadata, create DataRecord objects, add to db
    pass

def ingest_purchased_data(db: Session, file_path: str):
    """Placeholder for ingesting purchased data (CSV/Excel)."""
    print(f"Placeholder: Ingesting purchased data from: {file_path}")
    # Implementation using pandas (read_csv, read_excel) would go here
    # Process data, create DataRecord objects, add to db
    pass

def ingest_web_scrape(db: Session, url: str):
    """Placeholder for ingesting web-scraped data."""
    print(f"Placeholder: Ingesting scraped data from URL: {url}")
    # Implementation using libraries like requests and BeautifulSoup/Scrapy would go here
    # Fetch HTML, parse content, create DataRecord objects, add to db
    pass

def main():
    parser = argparse.ArgumentParser(description="Ingest data into the Karius database.")
    parser.add_argument("--source", required=True, choices=['who_csv', 'cdc_api', 'pubmed_api', 'purchased', 'web_scrape'], help="The data source type.")
    parser.add_argument("--path", help="Path to the data file (for file-based sources like who_csv, purchased).")
    parser.add_argument("--endpoint", help="API endpoint URL (for cdc_api).")
    parser.add_argument("--query", help="Query string or identifier (for pubmed_api).")
    parser.add_argument("--url", help="URL to scrape (for web_scrape).")

    args = parser.parse_args()
    db = get_db_session()

    try:
        if args.source == 'who_csv':
            if not args.path:
                print("Error: --path is required for source 'who_csv'")
                sys.exit(1)
            ingest_who_csv(db, args.path)
        elif args.source == 'cdc_api':
            if not args.endpoint:
                print("Error: --endpoint is required for source 'cdc_api'")
                sys.exit(1)
            ingest_cdc_api(db, args.endpoint)
        elif args.source == 'pubmed_api':
            if not args.query:
                print("Error: --query is required for source 'pubmed_api'")
                sys.exit(1)
            ingest_pubmed_api(db, args.query)
        elif args.source == 'purchased':
            if not args.path:
                print("Error: --path is required for source 'purchased'")
                sys.exit(1)
            ingest_purchased_data(db, args.path)
        elif args.source == 'web_scrape':
            if not args.url:
                print("Error: --url is required for source 'web_scrape'")
                sys.exit(1)
            ingest_web_scrape(db, args.url)
        else:
            print(f"Error: Unknown source '{args.source}'")
            sys.exit(1)
    finally:
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    main() 