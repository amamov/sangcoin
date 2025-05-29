import time
from typing import TypedDict, List
from utils import hash_data


class TxIO(TypedDict):
    owner: str
    amount: int


class Tx(TypedDict):
    id: str
    timestamp: int
    inputs: List[TxIO]
    outputs: List[TxIO]


def create_tx(inputs: List[TxIO], outputs: List[TxIO]) -> Tx:
    tx: Tx = {
        "id": "",
        "timestamp": int(time.time()),
        "inputs": inputs,
        "outputs": outputs,
    }
    tx["id"] = hash_data(tx)
    return tx
