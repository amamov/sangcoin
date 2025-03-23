import { server } from "./server";

const PORT = 7777;

const start = async () => {
  try {
    await server.listen({ port: PORT });
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
};

start();
