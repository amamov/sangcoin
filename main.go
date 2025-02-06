package main

import (
	"fmt"

	"github.com/amamov/sangcoin/blockchain"
)

func main() {

	bc := blockchain.GetBlockchain()

	fmt.Println(bc)

	chain := blockchain.GetBlockchain()
	chain.AddBlock("Second Block")
	chain.AddBlock("Third Block")
	for _, block := range chain.AllBlocks() {
		fmt.Printf("Data : %s\n", block.Data)
		fmt.Printf("Hash : %s\n", block.Hash)
		fmt.Printf("Prev Hash : %s\n", block.PrevHash)
		fmt.Println("---")
	}

	fmt.Println(chain.AllBlocks())

}
