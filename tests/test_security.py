import os
import sys
from datetime import timedelta
from jose import jwt
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from security import verify_password, get_password_hash, create_access_token  
from app.config import get_settings 

settings = get_settings()

def test_password_hashing():
    # 1. Arrange
    password = "supersecretpassword"
    
    # 2. Act
    hashed = get_password_hash(password)
    
    # 3. Assert
    assert password != hashed  # The hash should not equal the plain text!
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    # 1. Arrange
    subject_data = "test@example.com"
    
    # 2. Act
    token = create_access_token(subject=subject_data)
    
    # 3. Assert (We decode the token to verify it was signed with our secret)
    decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded  # Ensure it has an expiration time