const crypto = require("crypto");
const db = require("./db");
const utils = require("./utils");

class Block {
  /**@type {string}*/ data;
  /**@type {string}*/ hash;
  /**@type {string}*/ prevHash;
  /**@type {number} */ height;

  /**
   * @param {string} data
   * @param {string} prevHash
   * @param {number} height
   */
  async createBlock(data, prevHash, height) {
    this.data = data;
    this.prevHash = prevHash;
    this.height = height;
    const payload = this.data + this.prevHash + String(this.height);
    this.hash = crypto.createHash("sha256").update(payload).digest("hex");
    await this.persist();
  }

  async persist() {
    await db.saveBlock(this.hash, utils.bytesFrom(this));
  }
}

module.exports = Block;
