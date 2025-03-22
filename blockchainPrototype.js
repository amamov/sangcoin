const crypto = require("crypto");

class Block {
  /**@type {string}*/ data;
  /**@type {string}*/ hash;
  /**@type {string}*/ prevHash;
  /**@type {number} */ height;

  constructor(data, prevHash, height) {
    this.data = data;
    this.prevHash = prevHash;
    this.hash = this.calculateHash();
    this.height = height;
  }

  calculateHash() {
    const hashString = this.data + this.prevHash;
    return crypto.createHash("sha256").update(hashString).digest("hex");
  }
}

class Blockchain {
  /**@type {Block[]}*/ blocks;

  constructor() {
    if (!Blockchain.instance) {
      this.blocks = [];
      this.addBlock("Genesis Block");
      Blockchain.instance = this;
      Object.freeze(this);
    }
    return Blockchain.instance;
  }

  getLastHash() {
    if (this.blocks.length === 0) {
      return "";
    }
    return this.blocks[this.blocks.length - 1].hash;
  }

  /**
   * @param {string} data
   * @returns {Block}
   */
  createBlock(data) {
    const prevHash = this.getLastHash();
    const height = this.blocks.length + 1;
    return new Block(data, prevHash, height);
  }

  addBlock(data) {
    const newBlock = this.createBlock(data);
    this.blocks.push(newBlock);
  }

  allBlocks() {
    return this.blocks;
  }

  /**
   * @param {number} height
   * @returns {Block|null}
   */
  getBlock(height) {
    if (height <= 0 || height > this.blocks.length) {
      return null;
    }
    return this.blocks[height - 1];
  }
}

const blockchain = new Blockchain();

module.exports = blockchain;
