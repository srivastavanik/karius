# Karius Market Expansion AI Assistant

An AI-Driven Market Expansion & Partner Discovery tool for Karius, built around Novita's API (using Qwen 2.5 72B Instruct) with an embedding+vector-search layer. This application ingests global health/business data, surfaces unmet market needs, and recommends new partners.

## Architecture

```
┌──────────────┐       ┌──────────────┐       ┌───────────────┐
│  Data Sources│──►───▶│ Ingestion DB │──►───▶│ Vector Store  │
│ (CSV, APIs,  │       │ (Postgres)   │       │ (Pinecone)    │
│  Publications│       │              │       │               │
└──────────────┘       └──────────────┘       └───────────────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │ RAG Pipeline │
                                              │ (LangChain)  │
                                              └──────────────┘
                                                     │
                                                     ▼
┌───────────────┐        ┌──────────────────────┐    │    ┌──────────────┐
│  Front-End    │◀──────▶│  FastAPI Backend    │◀───┘───▶│ Novita LLM    │
│ (Streamlit)   │        │  • Retrieval        │         │ Qwen 2.5 72B  │
│               │        │  • LLM Orchestration│         │ Instruct via  │
└───────────────┘        └──────────────────────┘         │  API         │
                                                         └──────────────┘
```

## Features

- **Data Ingestion**: Import data from various sources (WHO, CDC, PubMed, etc.)
- **Vector Search**: Semantically search through ingested data using embeddings
- **RAG Pipeline**: Retrieval-Augmented Generation using LangChain and Novita's Qwen 2.5 72B
- **Interactive UI**: Streamlit frontend for querying the system and visualizing results
- **Market Analysis**: AI-driven insights for global market expansion
- **Partner Discovery**: Identification of potential partners and collaboration opportunities

## Project Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Novita API key
- Pinecone API key

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd karius-expansion-ai
   ```

2. **Setup using init script**
   ```bash
   chmod +x init.sh
   ./init.sh
   ```
   
   This script will:
   - Create a virtual environment
   - Install dependencies
   - Set up the database
   - Guide you through data ingestion and embedding generation
   - Start the application (optional)

### Manual Setup

1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy the example file: `cp .env.example .env`
   - Edit the `.env` file and add your API keys:
     - `NOVITA_API_KEY`: Your Novita API key
     - `PINECONE_API_KEY`: Your Pinecone API key
     - `PINECONE_ENVIRONMENT`: Your Pinecone environment (e.g., "us-west1-gcp")
     - `DATABASE_URL`: Your PostgreSQL connection string

4. **Set up the PostgreSQL database**
   - Create a database (e.g., `karius_db`) and a user with permissions
   - Create the schema: `python scripts/create_db.py`

5. **Ingest data**
   - Download or create sample data files in the `data/` directory
   - Run ingestion script: `python scripts/ingest.py --source who_csv --path data/your_file.csv`

6. **Generate embeddings**
   - Run embedding script: `python scripts/embed_and_store.py`

## Running the Application

### Using Docker (recommended for production)

```bash
# Start all services (PostgreSQL, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Manual Startup (development)

```bash
# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In a separate terminal, start the frontend
streamlit run app/ui.py
```

## Usage

1. Open the Streamlit UI in your browser: http://localhost:8501
2. Use the sidebar to select filters and query type
3. Enter your question in the text area or select from example questions
4. View the AI-generated answer and supporting sources
5. Explore the relationship visualization and key metrics

## API Endpoints

The backend exposes the following API endpoints:

- `GET /`: Basic API information
- `POST /query`: Submit a question to the AI assistant
- `GET /stats`: Get statistics about ingested data
- `GET /filters`: Get available metadata filters

## Data Sources

The system is designed to work with various data sources:

1. **WHO**: World Health Organization's Athena API
2. **CDC**: Centers for Disease Control and Prevention Open Data
3. **PubMed**: Medical research publications in BioC format
4. **Custom Data**: Purchased reports, web-scraped data, etc.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

[MIT License](LICENSE) 