import crypto from "crypto";
import { db } from "./db";
import { utils } from "./utils";

const difficulty: number = 2;

export default class Block {
  readonly data: string;
  readonly prevHash: string;
  readonly height: number;
  hash!: string;
  difficulty: number;
  nonce: number;

  constructor(data: string, prevHash: string, height: number) {
    this.data = data;
    this.prevHash = prevHash;
    this.height = height;

    this.difficulty = 2;
    this.nonce = 0;

    // const payload = this.data + this.prevHash + String(this.height);
    // this.hash = crypto.createHash("sha256").update(payload).digest("hex");
    this.mine();

    Object.freeze(this);
  }

  async persist(): Promise<void> {
    const bytes = utils.bytesFrom(this);
    await db.saveBlock(this.hash, bytes);
  }

  private mine() {
    const target = "0".repeat(this.difficulty);

    while (true) {
      const blockAsString = `${this.data}${this.prevHash}${this.nonce}`;
      const hash = crypto
        .createHash("sha256")
        .update(blockAsString)
        .digest("hex");

      console.log(`Block as String: ${blockAsString}`);
      console.log(`Hash: ${hash}`);
      console.log(`Target: ${target}`);
      console.log(`Nonce: ${this.nonce}\n\n`);

      if (hash.startsWith(target)) {
        this.hash = hash;
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
