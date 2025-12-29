from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import logging
import re

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA256"""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

def verify_password(hashed: str, password: str) -> bool:
    """Verify a password against its hash"""
    return check_password_hash(hashed, password)

def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    token = secrets.token_hex(length // 2)
    logger.debug(f"Generated token: {token}")
    return token

def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements"""
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )