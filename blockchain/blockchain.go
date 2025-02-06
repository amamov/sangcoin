package blockchain

import (
	"crypto/sha256"
	"fmt"
	"sync"
)

type block struct {
	Data     string
	Hash     string
	PrevHash string
}

type blockchain struct {
	blocks []*block // block 구조체의 주소를 저장하기 위해 (for 메모리 효율)
}

var bc *blockchain

var once sync.Once

func (b *block) calculateHash() {
	hash := sha256.Sum256([]byte(b.Data + b.PrevHash))
	b.Hash = fmt.Sprintf("%x", hash)
}

func (bc *blockchain) getLastHash() string {
	totalBlocks := len(bc.blocks)
	if totalBlocks == 0 {
		return ""
	}
	return bc.blocks[totalBlocks-1].Hash
}

func (bc *blockchain) createBlock(data string) *block {
	newBlock := block{data, "", bc.getLastHash()}
	newBlock.calculateHash()
	return &newBlock
}

func (bc *blockchain) AddBlock(data string) {
	bc.blocks = append(bc.blocks, bc.createBlock(data))
}

func GetBlockchain() *blockchain {
	if bc == nil {
		once.Do(func() {
			bc = &blockchain{}
			bc.AddBlock("Genesis Block")
		})

	}
	return bc
}

func (bc *blockchain) AllBlocks() []*block {
	return GetBlockchain().blocks
}
