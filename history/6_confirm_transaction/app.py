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


class BalanceResponse(BaseModel):
    address: str
    balance: int


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


@app.get("/balance/{address}")
def get_balance(address: str):
    return blockchain.get_utxos(address)


@app.get("/balance/total/{address}")
def get_balance_total(address: str):
    amount = blockchain.balance_by_address(address)
    return BalanceResponse(address=address, balance=amount)


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
