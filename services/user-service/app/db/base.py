# This file is the registry for Alembic

# import Base from session
from .session import Base

# import all models here so Alembic can discorver them for migrations
from ..models.user import User 

# This makes sure models are registered with Base metadata
__all__ = ["Base", "User"]