# Karius Market Expansion AI Assistant

This project implements an AI-driven tool to help Karius identify potential market expansion opportunities and discover relevant partners.

## Project Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd karius-expansion-ai
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    *   Copy the example file: `cp .env.example .env`
    *   Edit the `.env` file and add your actual API keys (Novita, Pinecone) and your PostgreSQL database connection string (`DATABASE_URL`).

5.  **Set up the PostgreSQL database:**
    *   Ensure you have PostgreSQL installed and running.
    *   Create a database (e.g., `karius_db`) and a user with permissions for that database, matching the details in your `.env` file.

6.  **Create the database schema:**
    ```bash
    python scripts/create_db.py
    ```

## Running the Application (Instructions TBD)

(More instructions will be added as components are built) 