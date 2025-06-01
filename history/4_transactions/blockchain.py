from typing import TYPE_CHECKING, Optional
from block import Block
from db import db
from utils import restore_buffer, bytes_from
from transactions import TxOut, UTXO

if TYPE_CHECKING:
    from transactions.mempool import Mempool

DEFAULT_DIFFICULTY = 2
DIFFICULTY_INTERVAL = 5
BLOCK_INTERVAL = 2
ALLOWED_RANGE_MINUTE = 2


class Blockchain:
    def __init__(self):
        self.last_hash = ""
        self.height = 0
        self.current_difficulty = DEFAULT_DIFFICULTY
        self._mempool: Optional[Mempool] = None

    def initialize(self):
        checkpoint = db.get_checkpoint()
        if checkpoint is None:
            self.add_block()
        else:
            self._restore(checkpoint)

    def set_mempool(self, mempool):
        self._mempool = mempool

    def get_mnempool(self) -> "Mempool":
        # TODO : setter, getter로 파이선스럽게 만들기 리팩토링
        if self._mempool is None:
            raise RuntimeError("mempool is not set.")
        return self._mempool

    def add_block(self):
        self.current_difficulty = self._calculate_difficulty()
        transactions = self.get_mnempool().confirm_tx()
        block = Block(
            prev_hash=self.last_hash,
            height=self.height + 1,
            difficulty=self.current_difficulty,
            transactions=transactions,
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

    # TODO :블록체인 폴더 만들어서 따로 빼서 나중에 리팩토링
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

    def get_utxos_by_address(self, address: str) -> list[UTXO]:
        """
        [[잔액 조회]]
        - 모든 블록의 트랜잭션을 순회하면서 해당 주소가 생성한 outputs중 아직 소비되지 않은 것만 UTXO로 간주
        - 소비여부는 두 가지로 판별
          1. 이후 어떤 트랜잭션의 inputs에 해당 tx의 id가 사용됨(즉, 이미 소비됨)
          2. Mempool에 들어있는 트랜잭션에서도 소비된 경우 고려

        ex1)
        📦 블록 #1: Genesis 블록 (coinbase only)
        tx0 = {
           "id": "tx0",
            "inputs": [ { "id": "", "index": -1, "owner": "COINBASE" } ],
            "outputs": [ { "owner": "sang_address", "amount": 50 } ]
        }

        📦 블록 #2: Sang → Alice 30 전송
        tx1 = {
            "id": "tx1",
            "inputs": [ { "id": "tx0", "index": 0, "owner": "sang_address" } ],
            "outputs": [
                { "owner": "alice_address", "amount": 30 },
                { "owner": "sang_address", "amount": 20 }  # change
            ]
        }

        📦 블록 #3: Alice → Bob 10 전송
        tx2 = {
            "id": "tx2",
            "inputs": [ { "id": "tx1", "index": 0, "owner": "alice_address" } ],
            "outputs": [
                { "owner": "bob_address", "amount": 10 },
                { "owner": "alice_address", "amount": 20 }  # change
            ]
        }

        get_utxos_by_address("sang_address")
        # → [ { "id": "tx1", "index": 1, "amount": 20 } ]

        get_utxos_by_address("alice_address")
        # → [ { "id": "tx2", "index": 1, "amount": 20 } ]

        get_utxos_by_address("bob_address")
        # → [ { "id": "tx2", "index": 0, "amount": 10 } ]

        ex2)
        📦 블록 #1: coinbase (Sang에게 50, Alice에게 20)
        tx0 = {
            "id": "tx0",
            "inputs": [ { "id": "", "index": -1, "owner": "COINBASE" } ],
            "outputs": [
                { "owner": "sang_address", "amount": 50 },
                { "owner": "alice_address", "amount": 20 }
            ]
        }
        블록을 채굴한 사람(Sang)은 채굴 보상 50 + 트랜잭션 수수료 20을 받았고,
        그 중 일부(20)를 다른 주소(Alice) 로 바로 보내고 싶었던 경우
        생성된 UTXO:
            tx0[0] → sang: 50
            tx0[1] → alice: 20

        📦 블록 #2: Sang → Alice에게 30 전송 (잔돈 20은 다시 Sang에게)
        tx1 = {
            "id": "tx1",
            "inputs": [ { "id": "tx0", "index": 0, "owner": "sang_address" } ],
            "outputs": [
                { "owner": "alice_address", "amount": 30 },
                { "owner": "sang_address", "amount": 20 }
            ]
        }
        UTXO 변화
            tx0[0] → 소모됨(spent)
            tx1[0] → alice: 30
            tx1[1] → sang: 20

        🔁 mempool에만 있는 트랜잭션: Sang → Alice에게 10 전송
        mempool_tx = {
            "id": "tx_mempool",
            "inputs": [ { "id": "tx1", "index": 1, "owner": "sang_address" } ],
            "outputs": [ { "owner": "alice_address", "amount": 10 } ]
        }
        sang의 tx1[1]은 블록에는 안 들어갔지만 mempool에서 사용 예정

        get_utxos_by_address("alice_address")
        # → [{ "id": "tx0", "index": 1, "amount": 20 }, { "id": "tx1", "index": 0, "amount": 30 }]

        """
        utxos: list[UTXO] = []
        spent_tx_ids = set()
        for block in self.blocks():
            for tx in block.transactions:
                for tx_in in tx["inputs"]:
                    if tx_in["owner"] == address:
                        spent_tx_ids.add((tx_in["id"], tx_in["index"]))

                for idx, tx_out in enumerate(tx["outputs"]):
                    if tx_out["owner"] == address:
                        if (tx["id"], idx) not in spent_tx_ids:
                            utxo: UTXO = {
                                "id": tx["id"],
                                "index": idx,
                                "amount": tx_out["amount"],
                            }
                            if not self.get_mnempool().is_utxo_used(utxo):
                                utxos.append(utxo)
        return utxos

    def balance_by_address(self, address: str) -> int:
        """
        balance는 특정 주소(address) 또는 계정(account) 이 현재 보유하고 있는 암호화폐의 양을 의미 (잔액)
        특정 Address 소유자가 가지고 있는 총액
        잔액은 "그 주소가 소유한 모든 UTXO의 합"으로 계산
        """
        utxos = self.get_utxos_by_address(address)
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
