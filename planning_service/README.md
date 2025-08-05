planning_service/
├── app/                            # Main application package
│   ├── __init__.py                 # Marks the folder as a Python package
│   ├── main.py                     # Entry point of the FastAPI app; loads routes and app instance
│
│   ├── api/                        # API route definitions (grouped by version)
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routes.py           # All API endpoints: outing preferences, plan management, recommendation
│
│   ├── core/                       # Core utilities and global configuration
│   │   ├── __init__.py
│   │   ├── config.py               # Loads environment variables (e.g., API keys, DB URIs)
│   │   └── mongo.py                # Initializes MongoDB client and handles link caching
│
│   ├── models/                     # Data models using Pydantic for validation and typing
│   │   ├── __init__.py
│   │   ├── outing.py               # Models for OutingPreferences and OutingProfile
│   │   └── plan.py                 # Model for Plan, which includes preferences and description
│
│   ├── services/                   # Business logic and integrations
│   │   ├── __init__.py
│   │   ├── google_places.py        # Handles geocoding, place search, details, and filtering by time
│   │   ├── selenium_reservation.py # Automates Ontopo search and scraping for booking links
│   │   └── recommendation.py       # Combines data sources to generate personalized recommendations
│
├── chromedriver.exe               # ChromeDriver for Selenium browser automation (used in Ontopo scraping)
├── .env                           # Environment variables (e.g., GOOGLE_API_KEY, MONGO_URI)
├── requirements.txt               # Python dependencies for the project
├── README.md                      # Project overview, setup, and documentation (you're editing this!)
