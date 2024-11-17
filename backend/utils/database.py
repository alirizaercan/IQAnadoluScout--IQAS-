# backend/utils/database.py
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None