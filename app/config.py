import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    database_url: str
    novita_api_key: str
    novita_embedding_model: str = "BAAI：BGE-M3"
    novita_llm_model: str = "qwen/qwen2.5-vl-72b-instruct"
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "karius-market"
    pinecone_embedding_dimension: int = 1024 # Default dimension for BGE-M3

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields from .env

settings = Settings() 