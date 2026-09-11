from sqlalchemy import Text, String, Column, Integer, DateTime
from sqlalchemy.sql import func
from database import Base

class Label(Base):
    __tablename__="labels"
    id=Column(Integer, primary_key=True, index=True)
    prompt=Column(Text, nullable=False)
    response_a=Column(Text,nullable=False)
    response_b=Column(Text, nullable=False)
    category=Column(String(255), nullable=False)
    annotator_id=Column(String(255),nullable=False)
    chosen=Column(String(50),nullable=True)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    labeled_at=Column(DateTime(timezone=True), nullable=True)
