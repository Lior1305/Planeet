import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Venue discovery configuration
VENUES_PER_TYPE = int(os.getenv("VENUES_PER_TYPE", "10"))  # Number of venues to get per venue type
MAX_TOTAL_VENUES = int(os.getenv("MAX_TOTAL_VENUES", "100"))  # Maximum total venues to discover
