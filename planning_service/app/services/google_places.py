import requests

GOOGLE_API_KEY = "AIzaSyCPVz2SxWPbfrilbZ2wo8KcSlBNa8uPYPM"
def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        raise Exception(f"Could not geocode the address: {data['status']}")


def search_places(lat, lng, place_type, keyword, radius=5000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "keyword": keyword,
        "language": "en",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data["status"] != "OK":
        print("No results or error:", data["status"])
        return []
    return data["results"]


def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,website,opening_hours",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get("result", {})

def is_place_open_at_time(opening_hours, target_datetime):
    if not opening_hours or "periods" not in opening_hours:
        return None
    day = target_datetime.weekday()
    time_str = target_datetime.strftime("%H%M")
    for period in opening_hours["periods"]:
        if period["open"]["day"] == day:
            open_time = period["open"]["time"]
            close_time = period.get("close", {}).get("time", "2359")
            if open_time <= time_str <= close_time:
                return True
    return False
