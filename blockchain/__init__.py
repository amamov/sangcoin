from dataclasses import dataclass
import hashlib
import threading
from typing import List


class Block:

    data: str
    hash: str
    prev_hash: str
    height: int

    def __init__(self, data, prev_hash, height):
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()
        self.height = height

    def calculate_hash(self):
        hash_string = (self.data + self.prev_hash).encode()
        return hashlib.sha256(hash_string).hexdigest()


class Blockchain:

    blocks: List[Block]

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.blocks = []
                    cls._instance.add_block("Genesis Block")
        return cls._instance

    def get_last_hash(self) -> str:
        return self.blocks[-1].hash if self.blocks else ""

    def create_block(self, data) -> Block:
        prev_hash = self.get_last_hash()
        height = len(Blockchain().blocks) + 1
        return Block(data, prev_hash, height)

    def add_block(self, data):
        self.blocks.append(self.create_block(data))

    def all_blocks(self) -> List[Block]:
        return self.blocks

    def get_block(self, height):
        try:
            return self.blocks[height - 1]
        except IndexError as e:
            return
