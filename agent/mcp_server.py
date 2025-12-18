import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from prompts.intent_classify import classify_intent_and_extract_params

app = FastAPI()


def book_table(date, time, restaurant_location, number_of_people):
    return f"Table booked in {restaurant_location} on {date} at {time} for {number_of_people} people. Thank you for choosing Good Foods. We look forward to serving you!"

def get_table_status(table_id, restaurant_location):
    return f"Table {table_id} in {restaurant_location} is confirmed."


def get_menu_details(restaurant_location):
    return f"Menu details for {restaurant_location} is available. We are a multi-cuisine restaurant. For more details, please visit our website to view the menu. www.goodfoods.com"

def classify_intent_and_trigger_logic(user_input: str) -> dict:
    """
    Core synchronous logic: given user_input, decide which function to call
    and return a plain Python dict message.
    """
    intent_info = classify_intent_and_extract_params(user_input)
    intent_json = json.loads(intent_info)
    function_name = intent_json.get("function")
    arguments = intent_json.get("arguments", {})

    if function_name == "book_table":
        print("book_table", arguments)
        message = book_table(
            date=arguments.get("date") or "Tomorrow",
            time=arguments.get("time") or "7:00 PM",
            restaurant_location=arguments.get("restaurant_location") or "New Delhi",
            number_of_people=arguments.get("number_of_people") or "2",
        )
        return {"status": "ok", "message": message}

    elif function_name == "get_table_status":
        message = get_table_status(
            table_id=arguments.get("table_id") or "123",
            restaurant_location=arguments.get("restaurant_location") or "New Delhi",
        )
        return {"status": "ok", "message": message}

    elif function_name == "get_menu_details":
        message = get_menu_details(
            restaurant_location=arguments.get("restaurant_location") or "New Delhi",
        )
        return {"status": "ok", "message": message}

    return {
        "status": "error",
        "message": "Could not classify intent or no matching function.",
    }


@app.post("/classify_intent_and_trigger")
async def classify_intent_and_trigger(request: Request):
    """
    FastAPI endpoint thin wrapper around the core sync logic.
    """
    data = await request.json()
    user_input = data.get("user_input", "")
    message = classify_intent_and_trigger_logic(user_input)
    print("message", message)

    return JSONResponse(message)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8001, reload=True)