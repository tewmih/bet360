from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..db.session import Base


class Listing(Base):
    __tablename__ = "listings"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Owner (references User Service)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(String(5000), nullable=True)

    # Value Objects (stored as JSON)
    location = Column(JSON, nullable=False)
    pricing = Column(JSON, nullable=False)
    property_details = Column(JSON, nullable=True)

    # Status
    status = Column(String(50), nullable=False, default="draft", index=True)
    verification_status = Column(String(50), nullable=False, default="pending", index=True)

    # Publication
    published_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Analytics
    view_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (will be added later)
    # media = relationship("Media", back_populates="listing", cascade="all, delete-orphan")
    # amenities = relationship("Amenity", secondary="listing_amenities", back_populates="listings")

    def __repr__(self):
        return f"<Listing(id={self.id}, title={self.title}, status={self.status})>"