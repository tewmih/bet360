from datetime import datetime
from typing import Any, Optional
import uuid

from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db.session import Base


class Listing(Base):
    __tablename__ = "listings"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Owner (references User Service)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Basic Information
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)

    # Value Objects (stored as JSON)
    location: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    pricing: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    property_details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )
    verification_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )

    # Publication
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships (will be added later)
    # media = relationship("Media", back_populates="listing", cascade="all, delete-orphan")
    # amenities = relationship("Amenity", secondary="listing_amenities", back_populates="listings")

    def __repr__(self):
        return f"<Listing(id={self.id}, title={self.title}, status={self.status})>"
