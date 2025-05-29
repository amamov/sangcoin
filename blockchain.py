from block import Block
from db import db
from utils import restore_buffer, bytes_from
from transactions import TxIO

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
            self.add_block()
        else:
            self._restore(checkpoint)

    def add_block(self):
        self.current_difficulty = self._calculate_difficulty()
        block = Block(
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

    def _tx_outputs(self) -> list[TxIO]:
        """
        블록체인에 있는 모든 거래 output들을 하나의 리스트로 리턴
        """
        outputs: list[TxIO] = []
        blocks = self.blocks()
        for block in blocks:
            for tx in block.transactions:
                outputs += tx["outputs"]
        return outputs

    def get_utxos(self, address: str) -> list[TxIO]:
        """
        특정 address로 블록체인에 있는 해당 사용자(address)의
        거래내역들(tx_outs)을 리턴
        """
        utxos: list[TxIO] = []
        outputs = self._tx_outputs()
        for output in outputs:
            if output["owner"] == address:
                utxos.append(output)
        return utxos

    def balance_by_address(self, address: str) -> int:
        """
        balance는 특정 주소(address) 또는 계정(account) 이 현재 보유하고 있는 암호화폐의 양을 의미 (잔액)
        특정 Address 소유자가 가지고 있는 총액
        잔액은 "그 주소가 소유한 모든 UTXO의 합"으로 계산산
        """
        utxos = self.get_utxos(address)
        amount: int = 0
        for utxo in utxos:
            amount += utxo["amount"]
        return amount

    def to_dict(self):
        return {
            "last_hash": self.last_hash,
            "height": self.height,
            "current_difficulty": self.current_difficulty,
        }


# Singleton
blockchain = Blockchain()
