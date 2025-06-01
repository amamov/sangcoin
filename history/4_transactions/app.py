from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from blockchain import blockchain
from block import Block
from utils import dict_from
from db import get_lmdb_contents
from transactions.mempool import mempool


app = FastAPI()
blockchain.set_mempool(mempool)
mempool.set_blockchain(blockchain)
blockchain.initialize()


class TxRequest(BaseModel):
    receiver: str
    amount: int


@app.get("/")
def root():
    return "hello blockchain"


@app.get("/status")
def get_status():
    return blockchain.to_dict()


@app.get("/blocks")
def get_blocks():
    blocks = blockchain.blocks()
    return dict_from(blocks)


@app.get("/blocks/{hash}")
def get_block_by_hash(hash: str):
    block = Block.get(hash)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Block not found"
        )
    return dict_from(block)


@app.post("/blocks", status_code=status.HTTP_201_CREATED)
def add_block():
    blockchain.add_block()
    return {"success": True}


@app.get("/balance/available/{address}")
def get_available_balance(address: str):
    """
    Confirmed + 사용되지 않은 UTXO 기준 실사용 가능 잔액
    """
    utxos = blockchain.get_utxos_by_address(address)
    return {
        "address": address,
        "balance_type": "available",
        "amount": sum(utxo["amount"] for utxo in utxos),
        "utxos": utxos,
    }


@app.get("/balance/projected/{address}")
def get_projected_balance(address: str):
    """
    Confirmed UTXO + mempool 내 잔돈(output)까지 포함한 예상 잔액
    """
    # 1. 확정된 UTXO 기준 사용 가능 금액
    utxos = blockchain.get_utxos_by_address(address)
    confirmed_amount = sum(utxo["amount"] for utxo in utxos)

    # 2. 아직 블록에 반영되지 않았지만, mempool에 있는 output 중 내가 받을 것
    pending_amount = 0
    for tx in mempool.txs:
        for out in tx["outputs"]:
            if out["owner"] == address:
                pending_amount += out["amount"]

    return {
        "address": address,
        "balance_type": "projected",
        "confirmed": confirmed_amount,
        "pending": pending_amount,
        "total": confirmed_amount + pending_amount,
        "mempool": mempool.txs,
        "utxos": utxos,
    }


@app.get("/mempool")
def get_mempool():
    return mempool.txs


@app.post("/transactions", status_code=status.HTTP_201_CREATED)
def transfer(tx_request: TxRequest):
    try:
        mempool.create_transfer(tx_request.receiver, tx_request.amount)
        return {"success": True}
    except ValueError:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction request",
        )


@app.get("/debug/db")
def debug_lmdb():
    return get_lmdb_contents()
