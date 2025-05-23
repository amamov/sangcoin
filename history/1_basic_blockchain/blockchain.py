import hashlib
from typing import List, Optional


class Block:
    def __init__(self, data: str, prev_hash: str, height: int):
        self.data = data
        self.prev_hash = prev_hash
        self.height = height
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        combined = self.data + self.prev_hash
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()


class Blockchain:

    def __init__(self):
        self.blocks: List[Block] = []
        self.add_block("Genesis Block")

    def get_last_hash(self) -> str:
        return self.blocks[-1].hash if self.blocks else ""

    def create_block(self, data: str) -> Block:
        prev_hash = self.get_last_hash()
        height = len(self.blocks) + 1
        return Block(data, prev_hash, height)

    def add_block(self, data: str):
        block = self.create_block(data)
        self.blocks.append(block)

    def all_blocks(self) -> List[Block]:
        return self.blocks

    def get_block(self, height: int) -> Optional[Block]:
        if 0 < height <= len(self.blocks):
            return self.blocks[height - 1]
        return None


blockchain = Blockchain()
