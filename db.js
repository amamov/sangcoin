const path = require("path");
const { Level } = require("level");

const DB_NAME = "blockchain.db",
  DB_PATH = path.join(__dirname, DB_NAME),
  DATA_SUB_NAME = "data",
  BLOCK_SUB_NAME = "blocks";

const level = new Level(DB_PATH, { valueEncoding: "json" });

const blocks = level.sublevel(BLOCK_SUB_NAME, { valueEncoding: "json" });
const datas = level.sublevel(DATA_SUB_NAME, { valueEncoding: "json" });

class Database {
  /**
   * @param {string} hash
   * @param {Buffer<ArrayBuffer>} data
   */
  async saveBlock(hash, data) {
    console.log(`Saving Block ${hash} \n data: ${data} \n`);
    await blocks.put(hash, data);
  }

  /**
   * @param {Buffer<ArrayBuffer>} data
   */
  async saveBlockchain(data) {
    console.log(`Update Blockchain ${data} \n`);
    await datas.put("checkpoint", data);
  }
}

const db = new Database();
Object.freeze(db);

module.exports = db;
