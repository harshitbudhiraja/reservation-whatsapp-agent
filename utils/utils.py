from dotenv import load_dotenv
import requests, os, json, base64, io
from PIL import Image
from agent.mcp_server import classify_intent_and_trigger_logic, book_table, get_table_status, get_menu_details
from utils.conversation_state import conversation_state
from prompts.parameter_extractor import extract_parameters
from utils.message_templates import FUNCTION_REQUIRED_PARAMS, get_missing_params_message

load_dotenv()
buffered = io.BytesIO()

BASE_URL = os.getenv("WHAPI_BASE_URL")
TOKEN = os.getenv("WHAPI_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def is_testing(number : str) -> bool:
    return number == "917838418898"

def get_opening_message():
    return "Hello! 👋\n\nWelcome to Good Foods Pvt Ltd!\n\n*How can we assist you today?*\n\n- Reserve your tables.\n- Browse through menus, ask queries.\n\nFeel free to share your queries. We look forward to serving you! Visit our website to view the menu. www.goodfoods.com 😊\n\nBest Regards,\n*Good Foods Pvt Ltd.*\nCustomer Service Team\n+91-9876543210"

def send_image_on_whatsapp(to, image_obj, caption: str = "Hello, How are you?"):

    url = f"{BASE_URL}/messages/image"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    image_obj.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{img_str}"

    payload = {
        "to": to,
        "caption": caption,
        "media": data_url
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "status": "error",
            "message": f"Failed to send image. Status code: {response.status_code}, Response: {response.text}"
        }

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

    user_id = msg.get("from", "default")

    try:
        # Check if there's an active session
        state = conversation_state.get_state(user_id)
        current_function = state.get("current_function")
        
        if current_function:
            # If session exists, directly call parameter extraction without intent classification
            missing_params = state.get("missing_params", [])
            collected_params = state.get("collected_params", {})
            
            if not missing_params:
                # If no missing params, treat as new intent
                mcp_result = classify_intent_and_trigger_logic(user_text, user_id)
            else:
                # Directly extract parameters
                param_result = extract_parameters(user_text, current_function, missing_params, collected_params)
                param_json = json.loads(param_result)
                extracted_arguments = param_json.get("arguments", {})
                
                # Merge extracted params with collected params
                merged_params = conversation_state.merge_params(user_id, extracted_arguments)
                conversation_state.update_state(user_id, collected_params=extracted_arguments)
                
                # Check if all required params are collected
                required_params = FUNCTION_REQUIRED_PARAMS.get(current_function, [])
                still_missing = [param for param in required_params if not merged_params.get(param) or merged_params.get(param) == ""]
                
                if still_missing:
                    # Still need more info
                    question_message = get_missing_params_message(current_function, still_missing)
                    conversation_state.update_state(user_id, missing_params=still_missing)
                    mcp_result = {"status": "need_info", "message": question_message, "function": current_function, "missing_params": still_missing}
                else:
                    # All params collected, execute function
                    mcp_result = _execute_function(current_function, merged_params, user_id)
        else:
            # If no session, call the full classify_intent_and_trigger_logic
            mcp_result = classify_intent_and_trigger_logic(user_text, user_id)
        
        print("mcp_result", mcp_result)
    except Exception:
        return get_opening_message()

    if not isinstance(mcp_result, dict):
        return get_opening_message()

    if mcp_result.get("status") == "need_info":
        return mcp_result.get("message", get_opening_message())

    if mcp_result.get("status") == "ok" and "message" in mcp_result:
        return mcp_result["message"]

    return get_opening_message()

def _execute_function(function_name: str, params: dict, user_id: str) -> dict:
    """Execute the function with collected parameters"""
    if function_name == "book_table":
        message = book_table(
            date=params.get("date"),
            time=params.get("time"),
            restaurant_location=params.get("restaurant_location"),
            number_of_people=params.get("number_of_people"),
        )
        conversation_state.clear_state(user_id)
        return {"status": "ok", "message": message}

    elif function_name == "get_table_status":
        message = get_table_status(
            table_id=params.get("table_id"),
            restaurant_location=params.get("restaurant_location"),
        )
        conversation_state.clear_state(user_id)
        return {"status": "ok", "message": message}

    elif function_name == "get_menu_details":
        message = get_menu_details(
            restaurant_location=params.get("restaurant_location"),
        )
        conversation_state.clear_state(user_id)
        return {"status": "ok", "message": message}
    
    return {
        "status": "error",
        "message": "Unknown function.",
    }

def send_message(payload):
    to = payload["messages"][0]["from"]
    from_me = payload["messages"][0]["from_me"]
    message = agent(payload)
    
    if from_me == False and is_testing(to):
        print("to", to)
        print("message", message)
        # send_message_on_whatsapp(to=to, message=message)

        media = Image.open("/Users/harshitbudhraja/Downloads/sarvam_assignment/wapp_distribution/assets/goodfoods.png")
        send_image_on_whatsapp(to=to, image_obj=media, caption=message)

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

