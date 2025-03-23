import crypto from "crypto";
import { db } from "./db";
import { utils } from "./utils";

export default class Block {
  readonly data: string;
  readonly prevHash: string;
  readonly height: number;
  readonly hash: string;

  constructor(data: string, prevHash: string, height: number) {
    this.data = data;
    this.prevHash = prevHash;
    this.height = height;

    const payload = this.data + this.prevHash + String(this.height);
    this.hash = crypto.createHash("sha256").update(payload).digest("hex");

    Object.freeze(this);
  }

  async persist(): Promise<void> {
    const bytes = utils.bytesFrom(this);
    await db.saveBlock(this.hash, bytes);
  }

  static async get(hash: string): Promise<Block | null> {
    const data = await db.block(hash);
    if (!data) return null;
    return utils.restoreBuffer(data);
  }
}
