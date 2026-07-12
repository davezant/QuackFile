# storage.py
import string
import secrets
import os
import time
from lib.constants import TEMP_PATH
from werkzeug.utils import secure_filename
def generate_token():
    characters = string.ascii_uppercase + string.digits
    first_half = ''.join(secrets.choice(characters) for _ in range(3))
    second_half = ''.join(secrets.choice(characters) for _ in range(3))
    return f"{first_half}-{second_half}"

def save_uploaded_file(file, token):
    if not file or not file.filename:
        return None
    ext = os.path.splitext(secure_filename(file.filename))[1]
    filename = f"{token}{ext}"
    file_path = os.path.join(TEMP_PATH, filename)
    file.save(file_path)
    return file_path

def save_text_payload(msg, token):
    if not msg:
        return None
    filename = f"{token}.txt"
    file_path = os.path.join(TEMP_PATH, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(msg)
    return file_path

