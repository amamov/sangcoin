from dataclasses import dataclass, field
import time
from typing import Optional
from db import db
from utils import bytes_from, restore_buffer, hash_data


@dataclass
class Block:
    data: str
    prev_hash: str
    height: int
    difficulty: int

    nonce: int = field(default=0, init=False)
    timestamp: int = field(default=0, init=False)
    hash: str = field(default="", init=False)

    def __post_init__(self):
        self._mine()
        self._persist()

    def _mine(self):
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
        return cls.from_dict(restore_buffer(data))

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        block = cls.__new__(cls)
        block.__dict__.update(data)
        return block
