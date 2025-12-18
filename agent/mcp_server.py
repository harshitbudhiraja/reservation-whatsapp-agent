from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from agent.agent_orchestrator import agent_orchestrator

app = FastAPI()


def book_table(date, time, restaurant_location, number_of_people):
    return f"Table booked in {restaurant_location} on {date} at {time} for {number_of_people} people. Thank you for choosing Good Foods. We look forward to serving you!"

def get_table_status(table_id, restaurant_location):
    return f"Table {table_id} in {restaurant_location} is confirmed."


def get_menu_details(restaurant_location):
    return f"Menu details for {restaurant_location} is available. We are a multi-cuisine restaurant. For more details, please visit our website to view the menu. www.goodfoods.com"

def classify_intent_and_trigger_logic(user_input: str, user_id: str) -> dict:
    return agent_orchestrator.process(user_input, user_id)


@app.post("/classify_intent_and_trigger")
async def classify_intent_and_trigger(request: Request):
    data = await request.json()
    user_input = data.get("user_input", "")
    user_id = data.get("user_id", "default")
    message = classify_intent_and_trigger_logic(user_input, user_id)
    print("message", message)

    return JSONResponse(message)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8001, reload=True)