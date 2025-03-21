import uvicorn
import api

if __name__ == "__main__":

    PORT = 7777

    uvicorn.run(api.app, host="localhost", port=PORT)
