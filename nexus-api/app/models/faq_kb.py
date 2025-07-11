from sqlalchemy import Column, String, Integer
from pgvector.sqlalchemy import Vector
from app.models.base import Base

class FAQKnowledgeBase(Base):
    __tablename__ = 'faq_knowledge_base'
    
    id = Column(Integer, primary_key=True, index=True)

    category = Column(String, nullable=False, index=True)
    text_chunk = Column(String, nullable=False)
    embedding = Column(Vector(1536), nullable=False)