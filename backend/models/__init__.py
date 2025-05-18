# backend/models/__init__.py
from sqlalchemy.ext.declarative import declarative_base

# Create a single declarative base for all models
Base = declarative_base()
