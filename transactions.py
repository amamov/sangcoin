import time
from dataclasses import dataclass, field
from typing import List
from utils import hash_dataclass


MINER_REWARD = 50


@dataclass
class TxIn:
    owner: str
    amount: int


@dataclass
class TxOut:
    owner: str
    amount: int


@dataclass
class Tx:
    id: str = field(default="", init=False)
    timestamp: int
    tx_ins: List[TxIn]
    tx_outs: List[TxOut]

    def __post_init__(self):
        self.id = hash_dataclass(self)


def make_coinbase_tx(address: str) -> Tx:
    """
    Conbase Transaction : 새 블록 안에서 가장 첫 번째 트랜젝션으로,
    채굴자에게 블록보상(새로운 코인 + 수수료)을 지급하기 위해 만들어진 트랜젝션
    -> 블록체인 네트워크에서 새로운 코인을 발행하려면 누군가에게 줘야 하는데,
    이 역할을 채굴자가 수행하고, 그 보상을 코인베이스 트랜젝션을 통해 지급 받는다.
    -> 신규 발행(Inflation) 기능 담당
    """
    tx_ins = [TxIn(owner="COINBASE", amount=MINER_REWARD)]
    tx_outs = [TxOut(owner=address, amount=MINER_REWARD)]
    return Tx(timestamp=int(time.time()), tx_ins=tx_ins, tx_outs=tx_outs)
