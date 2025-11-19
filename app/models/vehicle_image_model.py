from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class VehicleImage(Base):
    __tablename__ = "vehicle_images"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    url = Column(String, nullable=False)

    vehicle = relationship("Vehicle", back_populates="images")

    def __repr__(self):
        return f"<VehicleImage(id={self.id}, vehicle_id={self.vehicle_id})>"
