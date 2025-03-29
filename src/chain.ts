import Block from "./block";
import { db } from "./db";
import { utils } from "./utils";

const DEFAULT_DIFFICULTY = 2;
const DIFFICULTY_INTERVAL = 5; // 블럭 5개 생성될때마다 DIFF 조정
const BLOCK_INTERVAL = 2; // 2분마다 블럭이 1개씩 생성
const ALLOWED_RANGE = 2;

class Blockchain {
  lastHash!: string;
  height: number;
  currentDifficulty!: number;

  private static instance: Blockchain | null;

  constructor() {
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
      this.restore(checkpoint);
    }
  }

  async addBlock(data: string) {
    this.currentDifficulty = await this.difficulty();
    const block = new Block();
    await block.create({
      data,
      prevHash: this.lastHash,
      height: this.height + 1,
      difficulty: this.currentDifficulty,
    });
    this.lastHash = block.hash;
    this.height = block.height;
    await this.persist();
  }

  private restore(data: Buffer<ArrayBuffer>) {
    const restoredData = utils.restoreBuffer(data);
    this.height = restoredData.height;
    this.lastHash = restoredData.lastHash;
  }

  private async persist() {
    await db.saveBlockchain(utils.bytesFrom(this));
  }

  async blocks(): Promise<Block[]> {
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

  async difficulty(): Promise<number> {
    if (this.height === 0) {
      return DEFAULT_DIFFICULTY;
    } else if (this.height % DIFFICULTY_INTERVAL === 0) {
      return await this.recalculateDifficulty();
    } else {
      return this.currentDifficulty;
    }
  }

  async recalculateDifficulty(): Promise<number> {
    const allBlocks = await this.blocks();
    const lastBlock = allBlocks[0];
    const lastRecalculatedBlock = allBlocks[DIFFICULTY_INTERVAL - 1];
    const actualTime =
      (lastBlock.timestamp - lastRecalculatedBlock.timestamp) / 60;
    const expectedTime = DIFFICULTY_INTERVAL * BLOCK_INTERVAL;
    if (actualTime <= expectedTime - ALLOWED_RANGE) {
      return this.currentDifficulty + 1;
    } else if (actualTime >= expectedTime + ALLOWED_RANGE) {
      return this.currentDifficulty - 1;
    }
    return this.currentDifficulty;
  }
}

export const getBlockchain = async () => {
  return await Blockchain.getOrcreate();
};
