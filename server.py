from fastapi import FastAPI, Request
from utils.utils import send_message

app = FastAPI()

@app.get("")
async def root():
    return {"message": "Hello World"}


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    # print(payload)  
    try:
        send_message(payload)
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}

    return {"status": "ok"}

