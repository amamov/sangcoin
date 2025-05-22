import time
from typing import Optional
from db import db
from utils import bytes_from, restore_buffer, hash_data


class Block:
    def __init__(self):
        self.data: str = ""
        self.prev_hash: str = ""
        self.height: int = 0
        self.hash: str = ""
        self.difficulty: int = 0
        self.nonce: int = 0
        self.timestamp: int = 0

    def create(self, data: str, prev_hash: str, height: int, difficulty: int):
        self.data = data
        self.prev_hash = prev_hash
        self.height = height
        self.difficulty = difficulty
        self.nonce = 0
        self.timestamp = 0
        self.mine()
        self._persist()

    def mine(self):
        target = "0" * self.difficulty

        while True:
            self.timestamp = int(time.time())
            current_hash = hash_data(self)
            if current_hash.startswith(target):
                self.hash = current_hash
                break
            else:
                self.nonce += 1

    def _persist(self):
        data_bytes = bytes_from(self)
        db.save_block(self.hash, data_bytes)

    @classmethod
    def get(cls, hash: str) -> Optional["Block"]:
        data = db.get_block(hash)
        if not data:
            return None
        return restore_buffer(data)
