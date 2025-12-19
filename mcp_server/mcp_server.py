import os
import json
import redis
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from mcp_server.agent_orchestrator import agent_orchestrator
load_dotenv()

app = FastAPI()


@app.post("/classify_intent_and_trigger")
async def classify_intent_and_trigger(request: Request):
    data = await request.json()
    user_input = data.get("user_input", "")
    user_id = data.get("user_id", "default")
    message = agent_orchestrator.process(user_input, user_id)
    # print("message", message)

    return JSONResponse(message)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8001, reload=True)