from dotenv import load_dotenv
import requests, os, json, base64, io
from PIL import Image
from utils.conversation_state import conversation_state
from agents.parameter_extractor import extract_parameters
from utils.message_templates import FUNCTION_REQUIRED_PARAMS, get_missing_params_message
from mcp_server.agent_orchestrator import agent_orchestrator
from recommendation_system.rs import get_recommendation
from utils.booking_utils import book_table
from utils.whatsapp_utils import please_try_again, get_opening_message, send_message_on_whatsapp, send_image_on_whatsapp, is_testing, send_location_on_whatsapp

load_dotenv()
buffered = io.BytesIO()

def agent(payload):

    messages = payload.get("messages", [])
    user_id = payload.get("messages")[0].get("from", "default")
    user_text = messages[0].get("text", {}).get("body", "")

    if not user_text:
        return please_try_again()

    try:
        state = conversation_state.get_state(user_id)
        current_function = state.get("current_function")
        print("current_function", current_function)
        print("user_text", user_text)
        print("user_id", user_id)
        print("state", state)
        print("missing_params", state.get("missing_params", []))
        print("collected_params", state.get("collected_params", {}))
        
        
        if current_function:
            missing_params = state.get("missing_params", [])
            collected_params = state.get("collected_params", {})
            
            if not missing_params:
                mcp_result = agent_orchestrator.process(user_text, user_id)
            else:
                param_result = extract_parameters(user_text, current_function, missing_params, collected_params)
                param_json = json.loads(param_result)
                extracted_arguments = param_json.get("arguments", {})
                
                merged_params = conversation_state.merge_params(user_id, extracted_arguments)
                conversation_state.update_state(user_id, collected_params=merged_params)
                
                required_params = FUNCTION_REQUIRED_PARAMS.get(current_function, [])
                still_missing = [param for param in required_params if not merged_params.get(param) or merged_params.get(param) == ""]
                
                if still_missing:
                    question_message = get_missing_params_message(current_function, still_missing)
                    conversation_state.update_state(user_id, missing_params=still_missing)
                    mcp_result = {"status": "need_info", "message": question_message, "function": current_function, "missing_params": still_missing}
                else:
                    mcp_result = _execute_function(current_function, merged_params, user_id)
        else:
            mcp_result = agent_orchestrator.process(user_text, user_id)
        
    except Exception as e:
        print("Exception in agent", str(e))
        return please_try_again(str(e))

    if not isinstance(mcp_result, dict):
        print("mcp_result is not a dictionary")
        return please_try_again()

    if mcp_result.get("status") == "need_info":
        print("mcp_result is need_info")
        return mcp_result.get("message", please_try_again())

    if mcp_result.get("status") == "ok" and "message" in mcp_result:
        return mcp_result["message"]

    print("mcp_result is not ok")
    return get_opening_message()

def _execute_function(function_name: str, params: dict, user_id: str) -> dict:
    """Execute the function with collected parameters"""

    if function_name == "book_table":
        message = book_table(
            user_id=user_id,
            date=params.get("date"),
            time=params.get("time"),
            restaurant_location=params.get("restaurant_location"),
            number_of_people=params.get("number_of_people"),
        )
        conversation_state.clear_state(user_id)
        return {"status": "ok", "message": message}
    
    return {
        "status": "error",
        "message": "Unknown function.",
    }

def send_message(payload,send_image=False):
    to = payload["messages"][0]["from"]
    if not is_testing(to):
        return {"status": "success", "message": "Noise I'm in testing mode"}

    from_me = payload["messages"][0]["from_me"]
    location = payload["messages"][0]["location"] if "location" in payload["messages"][0] else None
    live_location = payload["messages"][0]["live_location"] if "live_location" in payload["messages"][0] else None
    location = location if location else live_location
    if location:
        user_lat = location["latitude"]
        user_long = location["longitude"]
        message, lat, long = get_recommendation(user_lat, user_long)
        send_location_on_whatsapp(to=to, latitude=lat, longitude=long)
        send_message_on_whatsapp(to=to, message=message)

        return {"status": "success", "message": "Message sent successfully"}

    message = agent(payload)
    
    if from_me == False and is_testing(to):
        send_message_on_whatsapp(to=to, message=message)
        # if send_image:
        #     media = Image.open("/Users/harshitbudhraja/Downloads/sarvam_assignment/wapp_distribution/assets/goodfoods.png")
        #     send_image_on_whatsapp(to=to, image_obj=media, caption=message)
        # else:

    else:
        return {"status": "success", "message": "Message sent successfully"}


