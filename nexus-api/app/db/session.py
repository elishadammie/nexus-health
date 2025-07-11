from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# The database URL needs to be constructed for SQLAlchemy
# Note: We are using 'postgresql+psycopg2' as the dialect
DATABASE_URL = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@db:5432/{settings.POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()