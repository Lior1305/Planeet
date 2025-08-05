from app.services.google_places import (
    geocode_address, search_places,
    get_place_details, is_place_open_at_time
)
from app.services.selenium_reservation import get_reservation_link
import random

def generate_recommendation(city, place_type, keywords, user_datetime):
    lat, lng = geocode_address(city)
    places = search_places(lat, lng, place_type, keywords)

    open_places = []
    for place in places[:10]:
        details = get_place_details(place["place_id"])
        if is_place_open_at_time(details.get("opening_hours", {}), user_datetime):
            open_places.append((place, details))

    if not open_places:
        return {"message": "No open places found"}

    place, details = random.choice(open_places)
    name = place.get("name", "Unknown")
    address = place.get("vicinity", "Unknown location")
    rating = place.get("rating", "N/A")
    total_reviews = place.get("user_ratings_total", 0)
    maps_link = f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}"
    website = details.get("website", "N/A")
    ontopo = get_reservation_link(name) if place_type == "restaurant" else None

    return {
        "name": name,
        "address": address,
        "rating": rating,
        "reviews": total_reviews,
        "website": website,
        "google_maps": maps_link,
        "ontopo_booking": ontopo
    }
