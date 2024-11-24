# backend/utils/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import Base
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.engine = None
        self.Session = None

    def connect(self):
        if self.engine is None:
            self.engine = create_engine(os.getenv('DATABASE_URL'))  # DATABASE_URL .env dosyasından alınacak
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        return self.Session()

    def close(self, session):
        session.close()