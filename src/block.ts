import { db } from "./db";
import { utils } from "./utils";
import { getBlockchain } from "./chain";

export default class Block {
  data!: string;
  prevHash!: string;
  height!: number;
  hash!: string;
  difficulty!: number;
  nonce!: number;
  timestamp!: number;

  async create(data: string, prevHash: string, height: number) {
    this.data = data;
    this.hash = "";
    this.prevHash = prevHash;
    this.height = height;

    const currentBlockchain = await getBlockchain();
    this.difficulty = await currentBlockchain.difficulty();

    this.nonce = 0;

    this.mine();
    await this.persist();
    Object.freeze(this);
  }

  private async persist(): Promise<void> {
    const bytes = utils.bytesFrom(this);
    await db.saveBlock(this.hash, bytes);
  }

  private mine() {
    const target = "0".repeat(this.difficulty);
    console.log("mine start");

    while (true) {
      this.timestamp = Math.floor(Date.now() / 1000);
      const hash = utils.hash(this);

      if (hash.startsWith(target)) {
        this.hash = hash;
        console.log(`Mined block with hash: ${hash}`);
        break;
      } else {
        this.nonce++;
      }
    }
  }

  static async get(hash: string): Promise<Block | null> {
    const data = await db.block(hash);
    if (!data) return null;
    return utils.restoreBuffer(data);
  }
}
