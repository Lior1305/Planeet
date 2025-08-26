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


def search_places(lat=None, lng=None, place_type=None, keyword=None, radius=5000, max_results=20):
    """
    Search for places using Google Places API with support for pagination
    
    Args:
        lat: Latitude
        lng: Longitude
        place_type: Google Places API type
        keyword: Search keyword
        radius: Search radius in meters
        max_results: Maximum number of results to return (default 20, max 60)
    
    Returns:
        List of places up to max_results
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    all_results = []
    page_token = None
    
    while len(all_results) < max_results:
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": place_type,
            "keyword": keyword,
            "language": "en",
            "key": GOOGLE_API_KEY
        }
        
        # Add pageToken if we have one
        if page_token:
            params["pagetoken"] = page_token
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] != "OK":
            print("No results or error:", data["status"])
            break
        
        # Add results from this page
        results = data.get("results", [])
        all_results.extend(results)
        
        # Check if there are more pages
        page_token = data.get("next_page_token")
        if not page_token:
            break
        
        # Google requires a short delay between page requests
        import time
        time.sleep(2)
    
    # Return up to max_results
    return all_results[:max_results]


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
