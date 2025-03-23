import path from "path";
import { Level } from "level";

const DB_NAME = "blockchain.db",
  DB_PATH = path.resolve(process.cwd(), DB_NAME),
  DATA_SUB_NAME = "data",
  BLOCK_SUB_NAME = "blocks",
  CHECKPOINT = "checkpoint";

class Database {
  level = new Level(DB_PATH, {
    valueEncoding: "buffer",
  });
  blocks = this.level.sublevel<string, Buffer>(BLOCK_SUB_NAME, {
    valueEncoding: "buffer",
  });
  datas = this.level.sublevel<string, Buffer>(DATA_SUB_NAME, {
    valueEncoding: "buffer",
  });

  async saveBlock(hash: string, data: Buffer<ArrayBuffer>) {
    console.log(`Saving Block ${hash} \n data: ${data} \n`);
    await this.blocks.put(hash, data);
  }

  async saveBlockchain(data: Buffer<ArrayBuffer>) {
    console.log(`Update Blockchain ${data} \n`);
    await this.datas.put(CHECKPOINT, data);
  }

  async checkpoint() {
    const data: Buffer<ArrayBuffer> | undefined =
      await this.datas.get(CHECKPOINT);
    return data;
  }

  async block(hash: string) {
    return await this.blocks.get(hash);
  }

  async close() {
    await this.level.close();
  }
}

export const db = Object.freeze(new Database());
