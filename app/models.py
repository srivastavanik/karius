from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB # Use JSONB for better performance/indexing in Postgres
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings # Import settings from config.py

Base = declarative_base()

class DataRecord(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True) # e.g., 'who', 'cdc', 'pubmed', 'statista', 'web_scrape'
    content = Column(Text) # Raw content (text chunk, JSON blob, etc.)
    metadata = Column(JSONB) # Flexible metadata (region, date, type, original_id, url, etc.)

    def __repr__(self):
        return f"<DataRecord(id={self.id}, source='{self.source}', metadata='{self.metadata}')>"

# Database connection setup (can be moved to a dedicated db module later if needed)
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 