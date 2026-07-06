import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database.base import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False) # e.g., "High", "Medium", "Low"
    input_features = Column(JSONB, nullable=True) # Stores the data sent to the ML model
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="predictions")
    reports = relationship("Report", back_populates="prediction")