import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=int(os.getenv("REDIS_DB")), password=os.getenv("REDIS_PASSWORD"))


def populate_redis_with_location_data():
    with open("location.json", "r") as f:
        location_map = json.load(f)

    for location_id, location_info in location_map.items():
        redis_key = f"available_capacity_{location_id}"
        for hour in range(24):
            redis_key = f"available_capacity_{location_id}_{hour}"
            redis_client.set(redis_key, location_info.get("total_capacity"))


def get_capacity(location_id: str, hour: int) -> int | str:
    redis_key = f"available_capacity_{location_id}_{hour}"
    available_seats = redis_client.get(redis_key)
    if available_seats is not None:
        try:
            available_seats = int(available_seats)
        except ValueError:
            available_seats = 0

    return available_seats



def list_all_redis_keys_and_values():
    """
    Prints all key-value pairs currently stored in the connected Redis database.
    """
    for key in redis_client.keys("*"):
        try:
            value = redis_client.get(key)
            print(f"{key.decode('utf-8')}: {value.decode('utf-8') if value else value}")
        except Exception as e:
            print(f"Error decoding key or value for: {key} ({e})")




if __name__ == "__main__":
    populate_redis_with_location_data()
    capacity = get_capacity(1,12)
    print(capacity)
    