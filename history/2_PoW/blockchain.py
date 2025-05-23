import time
from typing import List
from dataclasses import dataclass, field
from utils import hash_data

DEFAULT_DIFFICULTY = 2
DIFFICULTY_INTERVAL = 5
BLOCK_INTERVAL = 2
ALLOWED_RANGE_MINUTE = 2


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


class Blockchain:
    def __init__(self):
        self.blocks: List[Block] = []
        self.current_difficulty = DEFAULT_DIFFICULTY
        self.add_block("Genesis")

    def add_block(self, data: str):
        self.current_difficulty = self._calculate_difficulty()
        prev_hash = self.blocks[-1].hash if self.blocks else ""
        height = len(self.blocks) + 1
        block = Block(data, prev_hash, height, self.current_difficulty)
        self.blocks.append(block)

    def get_last_block(self) -> Block:
        return self.blocks[-1]

    def get_block(self, hash: str) -> Block | None:
        for block in self.blocks:
            if block.hash == hash:
                return block
        return None

    def _calculate_difficulty(self) -> int:
        height = len(self.blocks)
        if height == 0:
            return DEFAULT_DIFFICULTY
        if height % DIFFICULTY_INTERVAL != 0:
            return self.current_difficulty
        return self._recalculate_difficulty()

    def _recalculate_difficulty(self) -> int:
        if len(self.blocks) < DIFFICULTY_INTERVAL:
            return self.current_difficulty

        latest = self.blocks[-1]
        prev = self.blocks[-DIFFICULTY_INTERVAL]
        actual_time = (latest.timestamp - prev.timestamp) / 60
        expected_time = DIFFICULTY_INTERVAL * BLOCK_INTERVAL

        if actual_time < expected_time - ALLOWED_RANGE_MINUTE:
            return self.current_difficulty + 1
        if actual_time > expected_time + ALLOWED_RANGE_MINUTE:
            return self.current_difficulty - 1
        return self.current_difficulty


# 싱글 인스턴스 (모듈 전역에서 사용)
blockchain = Blockchain()
