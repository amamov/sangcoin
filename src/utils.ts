import * as crypto from "crypto";

class Utils {
  bytesFrom = (value: any) => {
    const buffer = Buffer.from(JSON.stringify(value));
    return buffer;
  };

  restoreBuffer = (buffer: Buffer<ArrayBufferLike>): any => {
    let str: string;

    if (Buffer.isBuffer(buffer)) {
      str = buffer.toString();
    } else {
      throw new Error("restoreBuffer: Input must be a Buffer!");
    }

    try {
      return JSON.parse(str);
    } catch (error) {
      console.error("restoreBuffer: JSON parse failed!", error);
      console.error("Data received:", str);
      throw error;
    }
  };

  hash = (value: any): string => {
    return crypto
      .createHash("sha256")
      .update(JSON.stringify(value))
      .digest("hex");
  };
}

export const utils = new Utils();
