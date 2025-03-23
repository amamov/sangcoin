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
}

export const utils = new Utils();
