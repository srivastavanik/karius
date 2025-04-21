#!/bin/bash

echo "Karius Market Expansion AI - Initialization Script"
echo "=================================================="

# Check if Python environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating and activating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Using existing virtual environment: $VIRTUAL_ENV"
fi

# Create the data directory if it doesn't exist
if [ ! -d "data" ]; then
    mkdir -p data
    echo "Created data directory."
fi

# Check if .env file exists, if not create from example
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env file from .env.example. Please edit it to add your API keys."
    else
        echo "WARNING: No .env.example file found. You need to create a .env file manually."
    fi
fi

# Prompt user for database setup
read -p "Do you want to set up the database? (y/n): " setup_db
if [ "$setup_db" = "y" ]; then
    echo "Creating database schema..."
    python scripts/create_db.py
    echo "Database schema created."
fi

# Prompt user for data ingestion
read -p "Do you want to ingest sample data? (y/n): " ingest_data
if [ "$ingest_data" = "y" ]; then
    echo "Ingesting sample data..."
    
    # Example of WHO data ingestion - assumes data/who_sample.csv exists
    # You would need to create or download this file
    if [ -f "data/who_sample.csv" ]; then
        python scripts/ingest.py --source who_csv --path data/who_sample.csv
    else
        echo "Sample WHO data file not found at data/who_sample.csv"
        echo "Please download or create a sample CSV file."
    fi
fi

# Prompt user for embedding
read -p "Do you want to generate embeddings for the ingested data? (y/n): " embed_data
if [ "$embed_data" = "y" ]; then
    echo "Generating embeddings and storing in Pinecone..."
    
    # Run the embedding script (will process all records in the database)
    python scripts/embed_and_store.py --batch-size 10
fi

# Prompt user to start the backend server
read -p "Do you want to start the FastAPI backend? (y/n): " start_backend
if [ "$start_backend" = "y" ]; then
    echo "Starting FastAPI backend on http://localhost:8000 ..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "You can start the backend manually with:"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    echo "You can start the Streamlit frontend with:"
    echo "  streamlit run app/ui.py"
    
    echo "Or use Docker Compose to start all services:"
    echo "  docker-compose up -d"
fi

echo "Initialization complete." 