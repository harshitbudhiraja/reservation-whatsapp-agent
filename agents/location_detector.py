from utils.openrouter import call_openrouter_llm
import json
import os

LOCATION_PATH = os.path.join(os.path.dirname(__file__), "../location.json")

def load_locations():
    with open(LOCATION_PATH, "r", encoding="utf-8") as f:
        locations_dict = json.load(f)

    return [loc for loc in locations_dict.values()]

def location_detector(user_input):

    locations = load_locations()
    location_descriptions = [
        f"{loc['name']} ({loc['address']}) [id: {loc['id']}]"
        for loc in locations
    ]
    # print("location_descriptions", location_descriptions)
    all_locations_str = "\n".join(location_descriptions)

    system_prompt = f"""
You are a highly accurate assistant specialized in mapping user-provided locations to the correct venue from the given list.

INSTRUCTIONS:
- ONLY map the user input to a location if there is a clear or close match between the input and either the NAME or ADDRESS of a location in the list below.
- If NO location name or address in the list closely or clearly matches the user input, reply with: {{"id": null, "name": null}}.
- STRICTLY use the locations in the list below. Do NOT make up names or ids or guess from partial information.
- "id" must be an integer value (like 1, 2, 3, ...) and should match the "id" field from the list.
- "name" must be exactly as shown in the list's "name" field.
- NEVER provide a location id or name that is not present in the list.
- Output ONLY in this JSON format (with no extra words or explanations): {{"id": <location_id>, "name": "<location_name>"}}
- If no match, output exactly: {{"id": None, "name": None}}
- Your output must always refer exactly and strictly to the data given in the 'AVAILABLE LOCATIONS' list.

AVAILABLE LOCATIONS:
{all_locations_str}
"""

    user_prompt = f"""User location: {user_input}\n\nRespond ONLY with the JSON for the matched location as per instructions."""

    llm_reply = call_openrouter_llm(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen/qwen3-8b",
        max_tokens=1000,
        temperature=0.01,
        top_p=0.95
    )
    print("llm_reply", llm_reply)
    try:
        data = json.loads(llm_reply)
        location_id = data.get("id", None)
        location_name = data.get("name", None)
    except Exception:
        location_id, location_name = None, None

    return location_id, location_name



if __name__ == "__main__":
    location_id, location_name = location_detector("Dwarka sector 12")
    print(location_id, location_name)

