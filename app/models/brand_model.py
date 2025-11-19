from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Brand(Base):
    
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    country = Column(String(50), nullable=True)
    logo_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    vehicles = relationship("Vehicle", back_populates="brand", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}')>"