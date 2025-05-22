from block import Block
from db import db
from utils import restore_buffer, bytes_from

DEFAULT_DIFFICULTY = 2
DIFFICULTY_INTERVAL = 5
BLOCK_INTERVAL = 2
ALLOWED_RANGE_MINUTE = 2


class Blockchain:
    def __init__(self):
        self.last_hash = ""
        self.height = 0
        self.current_difficulty = DEFAULT_DIFFICULTY

        checkpoint = db.get_checkpoint()
        if checkpoint is None:
            self.add_block("Genesis")
        else:
            self._restore(checkpoint)

    def add_block(self, data: str):
        self.current_difficulty = self._calculate_difficulty()
        block = Block(
            data=data,
            prev_hash=self.last_hash,
            height=self.height + 1,
            difficulty=self.current_difficulty,
        )
        self.last_hash = block.hash
        self.height = block.height
        db.save_blockchain(bytes_from(self))

    def _restore(self, data: bytes):
        restored = restore_buffer(data)
        self.height = restored["height"]
        self.last_hash = restored["last_hash"]
        self.current_difficulty = restored["current_difficulty"]

    def blocks(self) -> list[Block]:
        result = []
        cursor = self.last_hash
        while cursor:
            block = Block.get(cursor)
            if not block:
                break
            result.append(block)
            cursor = block.prev_hash
        return result

    def _calculate_difficulty(self) -> int:
        if self.height == 0:
            return DEFAULT_DIFFICULTY
        if self.height % DIFFICULTY_INTERVAL != 0:
            return self.current_difficulty
        return self._recalculate_difficulty()

    def _recalculate_difficulty(self) -> int:
        blocks = self.blocks()
        if len(blocks) < DIFFICULTY_INTERVAL:
            return self.current_difficulty

        latest = blocks[0]
        prev = blocks[DIFFICULTY_INTERVAL - 1]
        actual_time = (latest.timestamp - prev.timestamp) / 60
        expected_time = DIFFICULTY_INTERVAL * BLOCK_INTERVAL

        if actual_time < expected_time - ALLOWED_RANGE_MINUTE:
            return self.current_difficulty + 1
        if actual_time > expected_time + ALLOWED_RANGE_MINUTE:
            return self.current_difficulty - 1
        return self.current_difficulty


blockchain = Blockchain()
