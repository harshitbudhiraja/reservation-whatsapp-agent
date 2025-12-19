import json
import math
import os

LOCATION_FILE = os.path.join(os.path.dirname(__file__), "../location.json")

DEFAULT_LAT = 28.6315
DEFAULT_LONG = 77.2167

def load_locations():
    with open(LOCATION_FILE, "r", encoding="utf-8") as f:
        loc_data = json.load(f)
    return list(loc_data.values())


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = (math.sin(d_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def recommend_nearby_venues(user_lat=None, user_long=None, top_n=3):
    if user_lat is None or user_long is None:
        user_lat = DEFAULT_LAT
        user_long = DEFAULT_LONG

    locations = load_locations()
    venues_with_distance = []
    for loc in locations:
        lat = loc.get('lat')
        lon = loc.get('long')
        if lat is None or lon is None:
            continue
        distance = haversine(user_lat, user_long, lat, lon)
        loc_copy = dict(loc)
        loc_copy['distance_km'] = distance
        venues_with_distance.append(loc_copy)

    venues_with_distance.sort(key=lambda x: x['distance_km'])
    return venues_with_distance[:top_n]


def calculate_distance(lat1, long1, lat2, long2):
    return round(haversine(lat1, long1, lat2, long2), 2)


def get_recommendation(user_lat, user_long):
    """
    Return a neat and beautiful formatted text with the nearby venues and their distances.
    """
    top_nearby = recommend_nearby_venues(user_lat, user_long, 3)
    if not top_nearby:
        return "Sorry, no nearby venues found at the moment."

    template_lines = [
        "🌟 *Your Top 3 Nearby Venues* 🌟\n"
    ]

    for idx, near in enumerate(top_nearby, start=1):
        name = near.get('name', 'Unknown Venue')
        address = near.get('address', '')
        lat = near.get('lat')
        long = near.get('long')
        maps_link = f"https://maps.google.com/?q={lat},{long}"
        distance = calculate_distance(lat, long, user_lat, user_long)
        
        venue_lines = [
            f"*{idx}. {name}*",
            f"- 📍 Address: {address}" if address else "",
            f"- 📏 Distance: {distance} km",
            f"- 🗺️ [View on Google Maps]({maps_link})",
        ]
        template_lines.append("\n".join(line for line in venue_lines if line))
        template_lines.append("-" * 28)

    template_lines.append("\nLooking forward to serving you at any of our locations! 🥗🍽️")
    text = "\n".join(template_lines)
    return text, lat, long


if __name__ == "__main__":
    print(get_recommendation(28.5445, 77.1926))