import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db.session import Base

class User(Base):
    __tablename__ = "users"

    # identitiy
    id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)

    # personal information
    full_name = Column(String(255), nullable = False)
    email = Column(String(255), unique = True, index = True, nullable = False)
    phone_number = Column(String(20), unique = True, index = True, nullable = True)

    # Authentication
    hashed_password = Column(String(255), nullable = False)

    # Authorizations
    role = Column(String(50), default = "user") # tenant, owner, admin, borker

    # Trust and veriffication
    is_verified = Column(Boolean, default = False)
    is_active = Column(Boolean, default = True)
    trust_score = Column(Integer, default = 0)

    # Timestamps
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    updated_at = Column(DateTime(timezone = True), onupdate = func.now())

    # composite indexes for common queries
    __table_args__ = (
        Index('ix_users_email_active', 'email', 'is_active'),
        Index('ix_users_role_active', 'role', 'is_active')
    )

def __repr__(self):
    return f"<User(id={self.id}, email={self.email}, full_name={self.full_name}, role={self.role})>"
