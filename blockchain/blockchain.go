/*
GetBlockchain : blockchain 구조체를 리턴한다. (만일 없으면 초기화한다.) + 싱글톤 패턴을 사용한다.
blockchain은 메모리 효율을 위해 블럭의 주소를 저장한다.
AddBlock : blockchain에 블럭을 추가한다. (createBlock, getLastHash, calculateHash 함수를 사용한다.)
AllBlocks : blockchain의 모든 블럭 리스트를 리턴한다.
*/

package blockchain

import (
	"crypto/sha256"
	"fmt"
	"sync"
)

type Block struct {
	Data     string
	Hash     string
	PrevHash string
}

type blockchain struct {
	blocks []*Block
}

var bc *blockchain

var once sync.Once

func (b *Block) calculateHash() {
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

func (bc *blockchain) createBlock(data string) *Block {
	newBlock := Block{data, "", bc.getLastHash()}
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

func (bc *blockchain) AllBlocks() []*Block {
	return GetBlockchain().blocks
}
