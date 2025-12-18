from dotenv import load_dotenv
import requests, os, json

from agent.mcp_server import classify_intent_and_trigger_logic

load_dotenv()

BASE_URL = os.getenv("WHAPI_BASE_URL")
TOKEN = os.getenv("WHAPI_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_opening_message():
    return "Hello! 👋\n\nWelcome to Good Foods Pvt Ltd!\n\n*How can we assist you today?*\n\n- Reserve your tables.\n- Browse through menus, ask queries.\n\nFeel free to share your queries. We look forward to serving you! Visit our website to view the menu. www.goodfoods.com 😊\n\nBest Regards,\n*Good Foods Pvt Ltd.*\nCustomer Service Team\n+91-9876543210"


def agent(payload):

    messages = payload.get("messages", [])
    if not messages:
        return get_opening_message()

    msg = messages[0]

    user_text = (
        msg.get("text", {}).get("body")
        or msg.get("body")
        or ""
    )
    if not user_text:
        return get_opening_message()

    try:
        mcp_result = classify_intent_and_trigger_logic(user_text)
        print("mcp_result", mcp_result)
    except Exception:
        return get_opening_message()

    if not isinstance(mcp_result, dict) or mcp_result.get("status") != "ok":
        return get_opening_message()


    if isinstance(mcp_result, dict) and "message" in mcp_result:
        return mcp_result["message"]

    return json.dumps(mcp_result)

def send_message(payload):
    to = payload["messages"][0]["from"]
    from_me = payload["messages"][0]["from_me"]
    message = agent(payload)
    
    if from_me == False:
        print("to", to)
        print("message", message)
        send_message_on_whatsapp(to=to, message=message)
    else:
        return {"status": "success", "message": "Message sent successfully"}


def send_message_on_whatsapp(to,message):

    url = f"{BASE_URL}/messages/text"

    HEADERS = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    payload = {
        "to": to,
        "body": f'{message}'
    }

    response = requests.post(
        url,
        headers=HEADERS,
        json=payload  
    )

    # print("response", response.json())


    if response.status_code == 200:
        return {"status": "success", "message": "Message sent successfully"}
    else:
        return {"status": "error", "message": "Failed to send message"}

