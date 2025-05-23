from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from blockchain import blockchain
from block import Block
from db import get_lmdb_contents

app = FastAPI()


class BlockRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return "hello blockchain"


@app.get("/status")
def get_status():

    return {
        "height": blockchain.height,
        "last_hash": blockchain.last_hash,
        "current_difficulty": blockchain.current_difficulty,
    }


@app.get("/blocks")
def get_blocks():
    blocks = blockchain.blocks()
    return [block.__dict__ for block in blocks]


@app.get("/blocks/{hash}")
def get_block_by_hash(hash: str):
    block = Block.get(hash)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block.__dict__


@app.post("/blocks", status_code=201)
def add_block(request: BlockRequest):
    blockchain.add_block(request.message)
    return {"success": True}


@app.get("/debug/db")
def debug_lmdb():
    return get_lmdb_contents()
