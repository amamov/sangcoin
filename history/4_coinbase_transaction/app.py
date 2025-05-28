from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from blockchain import blockchain
from block import Block
from utils import dict_from
from db import get_lmdb_contents


app = FastAPI()


class BlockRequest(BaseModel):
    message: str


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
        raise HTTPException(status_code=404, detail="Block not found")
    return dict_from(block)


@app.post("/blocks", status_code=201)
def add_block(request: BlockRequest):
    blockchain.add_block()
    return {"success": True}


@app.get("/debug/db")
def debug_lmdb():
    return get_lmdb_contents()
