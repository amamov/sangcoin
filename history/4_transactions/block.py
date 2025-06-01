from dataclasses import dataclass, field
import time
from typing import Optional, List
from db import db
from utils import bytes_from, restore_buffer, hash_data
from transactions import Tx


@dataclass
class Block:
    prev_hash: str
    height: int
    difficulty: int
    transactions: List[Tx]

    nonce: int = field(default=0, init=False)
    timestamp: int = field(default=0, init=False)
    hash: str = field(default="", init=False)

    def __post_init__(self):
        self._mine()
        self._persist()

    def _mine(self):
        """
        Block 채굴. 현재 Blockchain 난이도에 따라 채굴을 진행
        """
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
        """
        Block을 DB에 바이너리 값으로 저장.
        """
        db.save_block(self.hash, bytes_from(self))

    @classmethod
    def get(cls, hash: str) -> Optional["Block"]:
        """
        Block의 Hash 값으로 DB로부터 Block 객체(dataclass)를 가져옴.
        """
        data = db.get_block(hash)
        if not data:
            return None
        return cls._from_dict(restore_buffer(data))

    @classmethod
    def _from_dict(cls, data) -> "Block":
        block = cls.__new__(cls)
        block.__dict__.update(data)
        return block
