const Block = require("./block");
const db = require("./db");
const utils = require("./utils");

class Blockchain {
  /**@type {string}*/ lastHash;
  /**@type {number} */ height;

  constructor() {
    if (!Blockchain.instance) {
      this.lastHash = "";
      this.height = 0;
      this.addBlock("Genesis").then(() => {
        Blockchain.instance = this;
        Object.freeze(this);
      });
    }
    return Blockchain.instance;
  }

  /**@param  {string} data */
  async addBlock(data) {
    const block = new Block();
    await block.createBlock(data, this.lastHash, this.height);
    this.lastHash = block.hash;
    this.height = block.height;
    await this.persist();
  }

  async persist() {
    await db.saveBlockchain(utils.bytesFrom(this));
  }
}

const blockchain = new Blockchain();

module.exports = blockchain;
