from models import User, UserCreate, UserLogin
from typing import Optional
from datetime import datetime
import hashlib
from fastapi import Request

users_db = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, email: str, password: str):
    if username in users_db:
        return False, 'Username already exists.'
    for user in users_db.values():
        if user['email'] == email:
            return False, 'Email already registered.'
    user = {
        'username': username,
        'email': email,
        'password': hash_password(password),
        'created_at': datetime.utcnow(),
        '2fa_enabled': True,
        '2fa_secret': 'MOCKSECRET',
    }
    users_db[username] = user
    return True, None

def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = users_db.get(username)
    if not user or user['password'] != hash_password(password):
        return None
    return user

def verify_2fa(user: dict, totp: str) -> bool:
    # Mock TOTP: accept '123456' as valid
    return totp == '123456'

def get_current_user(request: Request):
    username = request.cookies.get('user')
    if not username or username not in users_db:
        return None
    return users_db[username] 