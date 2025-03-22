const Fastify = require("fastify");
const blockchain = require("./blockchain");

const server = Fastify({ logger: true });

server.get("/", async () => {
  return "hello blockchain";
});

server.get("/blocks", async () => {
  return blockchain.allBlocks();
});

server.get("/blocks/:blockId", async (request, reply) => {
  const { blockId } = request.params;
  const block = blockchain.getBlock(parseInt(blockId));
  if (!block) {
    return reply.status(404).send({ error: "Block not found" });
  }
  return block;
});

server.post(
  "/blocks",
  {
    schema: {
      body: {
        type: "object",
        required: ["message"],
        properties: {
          message: { type: "string" },
        },
      },
    },
  },
  async (request) => {
    const { message } = request.body;
    console.log(message);
    blockchain.addBlock(message);
    return blockchain.allBlocks();
  }
);

// 서버 실행

module.exports = server;
