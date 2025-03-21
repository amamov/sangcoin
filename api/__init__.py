from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

import blockchain

app = FastAPI()


class BlockData(BaseModel):
    message: str


@app.get("/")
def read_blocks():
    blockchain.Blockchain().blocks = []
    return blockchain.Blockchain().all_blocks()


@app.get("/blocks")
def read_blocks():
    return blockchain.Blockchain().all_blocks()


@app.post("/blocks")
async def create_block(data: BlockData):
    blockchain.Blockchain().add_block(data.message)
    return blockchain.Blockchain().all_blocks()


@app.get("/blocks/{block_id}")
def read_blocks(block_id: int):
    return blockchain.Blockchain().get_block(block_id)
