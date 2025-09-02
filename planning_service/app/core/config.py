import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Service URLs - can be overridden by environment variables
VENUES_SERVICE_URL = os.getenv("VENUES_SERVICE_URL", "http://venues-service:8000")
OUTING_PROFILE_SERVICE_URL = os.getenv("OUTING_PROFILE_SERVICE_URL", "http://outing-profile-service:5000")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users-service:8080")
UI_SERVICE_URL = os.getenv("UI_SERVICE_URL", "http://planeet-ui:80")
