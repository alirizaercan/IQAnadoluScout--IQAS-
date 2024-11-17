# backend/services/auth_service.py
from argon2 import PasswordHasher
from utils.database import Database
from datetime import datetime

class AuthService:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.connect()
        self.ph = PasswordHasher()

    def register(self, data):
        cursor = self.conn.cursor()
        username = data['username']
        email = data['email']
        password = self.ph.hash(data['password'])

        try:
            cursor.execute("""
                INSERT INTO users (username, email, password, created_at)
                VALUES (%s, %s, %s, %s)
            """, (username, email, password, datetime.now()))
            self.conn.commit()
            return {"message": "User registered successfully", "status": 201}
        except Exception as e:
            self.conn.rollback()
            return {"message": str(e), "status": 400}

    def login(self, data):
        cursor = self.conn.cursor()
        email = data['email']
        password = data['password']

        cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and self.ph.verify(user[1], password):
            return {"message": "Login successful", "user_id": user[0], "status": 200}
        return {"message": "Invalid credentials", "status": 401}
