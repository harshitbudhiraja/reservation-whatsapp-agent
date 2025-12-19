import os
import json
import redis
from dotenv import load_dotenv
load_dotenv()
from agents.location_detector import location_detector
from agents.time_extractor import time_to_hour_agent
from utils.whatsapp_utils import send_location_on_whatsapp

redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=int(os.getenv("REDIS_DB")), password=os.getenv("REDIS_PASSWORD"))

with open(os.path.join(os.path.dirname(__file__), "../location.json"), "r") as f:
    location_map = json.load(f)

def get_coordinates(location_id):
    latitude, longitude = location_map.get(location_id).get("latitude"), location_map.get(location_id).get("longitude")
    return latitude, longitude

def update_redis_value(key, value):
    redis_client.set(key, value)
    return True

def get_capacity(location_id, hour_int) -> int | str:
    
    redis_key = f"available_capacity_{location_id}_{hour_int}"
    available_seats = redis_client.get(redis_key)

    print("redis_key", redis_key)
    print("available_seats", available_seats)

    if available_seats is not None:
        try:
            available_seats = int(available_seats)
        except ValueError:
            available_seats = 0
    else:
        available_seats = 0
    return available_seats


def get_location_id(location_name):
    location_id, location_name = location_detector(location_name)
    if location_name is None or location_id is None:
        print("location_name is None or location_id is None")
        # TODO: Remove hardcoding, ask the user to provide the location again.
        return 10
    return location_id


def get_hour_int(time):
    hour_int = time_to_hour_agent(time)
    if hour_int is None:
        # TODO: Remove hardcoding, ask the user to provide the time again.
        return 10
    hour_int = int(hour_int)
    print("hour_int", hour_int, "(type: ", type(hour_int), ")")
    return hour_int

def book_table(user_id, date, time, restaurant_location, number_of_people):

    location_id = get_location_id(restaurant_location)
    hour_int = get_hour_int(time)

    print("location_id", location_id)
    print("hour_int", hour_int)
    capacity = get_capacity(location_id, hour_int)

    if int(capacity) < int(number_of_people):
        return f"❌ Sorry, we don't have enough capacity at {restaurant_location} for the given time. Please try a different location or time."

    redis_key = f"available_capacity_{location_id}_{hour_int}"
    update_redis_value(redis_key, int(capacity) - int(number_of_people))
    
    try:
        latitude, longitude = get_coordinates(location_id)
        send_location_on_whatsapp(to=user_id, latitude=latitude, longitude=longitude)
    except Exception as e:
        print("Error in sending location on whatsapp", str(e))

    return f"✅ Table booked successfully!\n\n📍 Location: {restaurant_location} (Capacity: {capacity} people)\n📅 Date: {date}\n🕐 Time: {time}\n👥 Guests: {number_of_people} people\n\n*Note:* We take reservations on an hourly basis.\n\nThank you for choosing Good Foods. We look forward to serving you! 😊"

