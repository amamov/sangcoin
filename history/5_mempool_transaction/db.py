import lmdb
import os
from typing import Optional

DB_NAME = "blockchain.db"
DB_PATH = os.path.join(os.getcwd(), DB_NAME)
BLOCK_PREFIX = b"blocks:"
DATA_PREFIX = b"data:"
CHECKPOINT_KEY = b"checkpoint"


class Database:
    def __init__(self, path: str = DB_PATH):
        self.store = lmdb.open(path, map_size=10**9)

    def _key(self, prefix: bytes, key: str) -> bytes:
        return prefix + key.encode("utf-8")

    def save_block(self, block_hash: str, block_data: bytes):
        with self.store.begin(write=True) as tx:
            tx.put(self._key(BLOCK_PREFIX, block_hash), block_data)

    def get_block(self, block_hash: str) -> Optional[bytes]:
        with self.store.begin() as tx:
            return tx.get(self._key(BLOCK_PREFIX, block_hash))

    def save_blockchain(self, checkpoint_data: bytes):
        with self.store.begin(write=True) as tx:
            tx.put(self._key(DATA_PREFIX, CHECKPOINT_KEY.decode()), checkpoint_data)

    def get_checkpoint(self) -> Optional[bytes]:
        with self.store.begin() as tx:
            return tx.get(self._key(DATA_PREFIX, CHECKPOINT_KEY.decode()))

    def close(self):
        self.store.close()


db = Database()


def get_lmdb_contents() -> list[dict]:
    contents = []

    with db.store.begin() as tx:
        for key, value in tx.cursor():
            k = key.decode("utf-8", errors="ignore")
            try:
                v = value.decode("utf-8", errors="ignore")
            except Exception:
                v = str(value)
            contents.append({"key": k, "value": v})

    return contents
