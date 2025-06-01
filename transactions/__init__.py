import time
from typing import TypedDict, List
from utils import hash_data


class TxIn(TypedDict):
    id: str
    index: int
    owner: str


class TxOut(TypedDict):
    owner: str
    amount: int


class UTXO(TypedDict):
    id: str
    index: int
    amount: int


class Tx(TypedDict):
    id: str
    timestamp: int
    inputs: List[TxIn]
    outputs: List[TxOut]


def create_tx(inputs: List[TxIn], outputs: List[TxOut]) -> Tx:
    tx: Tx = {
        "id": "",
        "timestamp": int(time.time()),
        "inputs": inputs,
        "outputs": outputs,
    }
    tx["id"] = hash_data(tx)
    return tx
