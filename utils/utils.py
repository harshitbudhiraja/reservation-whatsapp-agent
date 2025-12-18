from dotenv import load_dotenv
import requests,os,json
load_dotenv()

BASE_URL = os.getenv("WHAPI_BASE_URL")
TOKEN = os.getenv("WHAPI_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_opening_message():
    """
    *Hello! 👋*

        Welcome to Good Foods Pvt Ltd!

        *How can we assist you today?*

        - Reserve your tables.
        - Browse through menus, ask queries.

        Feel free to share your queries. We look forward to serving you! 😊

        Best Regards,
        *Good Foods Pvt Ltd.*
        Customer Service Team
        +91-9876543210
    """


def agent(payload):
    # if first message, return opening message -> return opening message
    # if user content is "stop", return stop message -> return stop message
    # user asks for reservation, return reservation message -> return reservation message
    # user asks for menu, return menu message -> return menu message
    # user asks for contact/info, return contact message -> return contact message
    # user asks for cancellation, return cancellation message -> return cancellation message
    return get_opening_message()

def send_message(payload):
    to = payload["messages"][0]["from"]
    from_me = payload["messages"][0]["from_me"]
    print("to", to)
    message = agent(payload)

    print(payload)
    if from_me == False :
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
        "body": f'{message}',
        "media": "/Users/harshitbudhraja/Downloads/sarvam_assignment/wapp_distribution/assets/image.png"
    }

    response = requests.post(
        url,
        headers=HEADERS,
        json=payload  
    )

    print("response", response.json())


    if response.status_code == 200:
        return {"status": "success", "message": "Message sent successfully"}
    else:
        return {"status": "error", "message": "Failed to send message"}

