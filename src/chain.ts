import Block from "./block";
import { db } from "./db";
import { utils } from "./utils";

class Blockchain {
  lastHash!: string;
  height!: number;

  private static instance: Blockchain | null;

  constructor() {
    this.lastHash = "";
    this.height = 0;
  }

  static async getOrcreate() {
    if (this.instance) return this.instance;

    const instance = new Blockchain();
    await instance.init();

    Blockchain.instance = instance;
    return instance;
  }

  private async init() {
    const checkpoint = await db.checkpoint();
    if (!checkpoint) {
      await this.addBlock("Genesis");
    } else {
      const restoredData = utils.restoreBuffer(checkpoint);
      this.height = restoredData.height;
      this.lastHash = restoredData.lastHash;
    }
  }

  async addBlock(data: string) {
    const block = new Block(data, this.lastHash, this.height + 1);
    await block.persist();
    this.lastHash = block.hash;
    this.height = block.height;
    await this.persist();
  }

  private async persist() {
    await db.saveBlockchain(utils.bytesFrom(this));
  }

  async blocks() {
    const blocks: Block[] = [];
    let hashCursor = this.lastHash;

    while (hashCursor) {
      const block = await Block.get(hashCursor);
      if (!block) {
        break;
      }
      blocks.push(block);
      hashCursor = block.prevHash;
      if (!hashCursor) {
        break;
      }
    }

    return blocks;
  }
}

export const getBlockchain = async () => {
  return await Blockchain.getOrcreate();
};
