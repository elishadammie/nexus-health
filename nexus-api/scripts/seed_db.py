import os
import httpx
from sqlalchemy import text # Import the 'text' function
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.base import Base
from app.models.faq_kb import FAQKnowledgeBase
from app.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

KB_PARENT_PATH = "knowledge_base/"

def load_and_process_docs(db_session: Session, category: str):
    """Loads, processes, and stores docs for a specific category."""
    category_path = os.path.join(KB_PARENT_PATH, category)
    if not os.path.exists(category_path):
        return 0

    documents = []
    for filename in os.listdir(category_path):
        filepath = os.path.join(category_path, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(filepath)
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath)
        else:
            continue
        print(f"Loading '{category}' doc: {filename}")
        documents.extend(loader.load())

    if not documents:
        return 0

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    
    insecure_client = httpx.Client(verify=False)
    embeddings_model = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY, http_client=insecure_client)
    
    text_chunks = [chunk.page_content for chunk in chunks]
    embeddings = embeddings_model.embed_documents(text_chunks)
    
    kb_entries = []
    for i, chunk_text in enumerate(text_chunks):
        entry = FAQKnowledgeBase(category=category, text_chunk=chunk_text, embedding=embeddings[i])
        kb_entries.append(entry)
        
    db_session.add_all(kb_entries)
    db_session.commit()
    return len(kb_entries)

def seed_database():
    """Initializes the DB, enables pgvector, and seeds the knowledge base."""
    print("Starting database seeding...")
    
    # NEW: Connect to the engine and enable the pgvector extension
    with engine.connect() as conn:
        print("Enabling the 'vector' extension in PostgreSQL...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # Create table schema
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        if db.query(FAQKnowledgeBase).first():
            print("Database already contains data. To re-seed, clear the table first.")
            return

        faq_count = load_and_process_docs(db, "faq")
        print(f"Successfully added {faq_count} FAQ entries.")
        
        triage_count = load_and_process_docs(db, "triage")
        print(f"Successfully added {triage_count} Triage entries.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()