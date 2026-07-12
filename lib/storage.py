# storage.py
import requests
from constants import StorageType

class Blob:
    def __init__(self, Storage: StorageType):
        self.Storage = Storage

    def send_file(self):
        pass

    def get_file(self, hash: str):
        pass
