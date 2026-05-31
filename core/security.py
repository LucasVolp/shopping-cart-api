import bcrypt


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain text password against its bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())
