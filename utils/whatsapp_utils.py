from dotenv import load_dotenv
import requests, os, json, base64, io
from PIL import Image
from utils.conversation_state import conversation_state
from agents.parameter_extractor import extract_parameters
from utils.message_templates import FUNCTION_REQUIRED_PARAMS, get_missing_params_message
from recommendation_system.rs import get_recommendation

load_dotenv()
BASE_URL = os.getenv("WHAPI_BASE_URL")
TOKEN = os.getenv("WHAPI_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def is_testing(number : str) -> bool:
    return number == "917838418898"

def please_try_again(e=None) -> str:
    print("error in please_try_again", e)
    return f"The System encountered an error with the input provided. Please try again.\n\n*Try: Reserve a table for 2 people at 6 PM in Lajpat Nagar:*"

def get_opening_message() -> str:
    return "Hello! 👋\n\nWelcome to Good Foods Pvt Ltd!\n\n*How can we assist you today?*\n\n- Reserve your tables.\n- Ask queries.\n\nFeel free to share your queries.\n\n*Share you whatsapp location to get the nearest venue to you.*\n\nWe look forward to serving you! Visit our website to view the menu. www.goodfoods.com 😊\n\nBest Regards,\n*Good Foods Pvt Ltd.*\nCustomer Service Team\n+91-9876543210"

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


def send_message_on_whatsapp(to,message : str) -> dict:

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


    if response.status_code == 200:
        return {"status": "success", "message": "Message sent successfully"}
    else:
        return {"status": "error", "message": "Failed to send message"}


def send_location_on_whatsapp(to, latitude, longitude, text=None):
    url = f"{BASE_URL}/messages/location"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }
    payload = {
        "to": to,
        "latitude": latitude,
        "longitude": longitude,
        "name": text
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return {"status": "success", "message": "Location sent successfully"}
    else:
        return {"status": "error", "message": f"Failed to send location. Status code: {response.status_code}, Response: {response.text}"}

if __name__ == "__main__":
    send_message_on_whatsapp("917838418898", "Hello, How are you?")