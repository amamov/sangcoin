import Fastify, {
  FastifyInstance,
  FastifyReply,
  FastifyRequest,
} from "fastify";
import { getBlockchain } from "./chain";
import Block from "./block";

export const server: FastifyInstance = Fastify({ logger: true });

server.get("/", async (request: FastifyRequest, reply: FastifyReply) => {
  return "hello blockchain";
});

server.get("/blocks", async (request: FastifyRequest, reply: FastifyReply) => {
  const blockchain = await getBlockchain();
  return blockchain.blocks();
});

server.get<{ Params: { hash: string } }>(
  "/blocks/:hash",
  async (request, reply) => {
    const { hash } = request.params;
    const block = await Block.get(hash);
    if (!block) {
      return reply.status(404).send({ error: "Block not found" });
    }
    return block;
  }
);

server.post<{
  Body: { message: string };
}>(
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
  async (request, reply) => {
    const { message } = request.body;
    const blockchain = await getBlockchain();
    await blockchain.addBlock(message);

    return reply.status(201).send({ success: true });
  }
);
