# ecrypt.py
from cryptography.fernet import Fernet

def generate_key() -> bytes:
    return Fernet.generate_key()

def encrypt_data(data: bytes, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.encrypt(data)

def decrypt_data(data: bytes, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.decrypt(data)
