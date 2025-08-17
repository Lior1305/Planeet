# Venues Service

A comprehensive FastAPI service for managing venues with advanced search and filtering capabilities. This service provides a complete API for discovering, creating, and managing places with location-based search, ratings, amenities, link management, and **personalized recommendations** based on user preferences from the Planning Service.

## 🎯 **Features**

- **Venue Management**: Full CRUD operations for venues
- **Advanced Search**: Filter by venue type, location, rating, price range, amenities
- **Location-based Search**: Radius-based venue discovery using coordinates
- **Link Management**: Add, update, and manage venue links (websites, booking, social media)
- **Personalized Search**: AI-powered venue recommendations based on user preferences
- **Planning Service Integration**: Generate comprehensive outing plans with venue suggestions
- **Real-time Updates**: Status notifications and progress tracking during plan generation
- **Google Places Integration**: Real-time venue discovery using Google Places API

## API Endpoints

### Venues

- `POST /api/v1/venues` - Create a new venue
- `GET /api/v1/venues` - Get all venues with filtering and pagination
- `GET /api/v1/venues/{venue_id}` - Get a specific venue
- `PUT /api/v1/venues/{venue_id}` - Update a venue
- `DELETE /api/v1/venues/{venue_id}` - Delete a venue

### Link Management

- `POST /api/v1/venues/{venue_id}/links` - Add a new link to a venue
- `GET /api/v1/venues/{venue_id}/links` - Get all links for a venue
- `PUT /api/v1/venues/{venue_id}/links/{link_index}` - Update a specific link
- `DELETE /api/v1/venues/{venue_id}/links/{link_index}` - Delete a specific link

### Search & Recommendations

- `POST /api/v1/search` - Advanced search with multiple criteria
- `POST /api/v1/search/personalized` - **Personalized search using user preferences**
- `GET /api/v1/search/quick` - Quick text-based search
- `GET /api/v1/recommendations/{user_id}` - **Get personalized venue recommendations**

### Utility

- `GET /api/v1/venue-types` - Get all available venue types
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Service statistics

## Data Models

### Venue Types
- restaurant, bar, cafe, museum, theater, park, shopping_center, sports_facility, hotel, other

### Location
- latitude, longitude, address, city, country

### Venue Links
- **type**: Type of link (website, social_media, booking, menu, etc.)
- **url**: The actual URL
- **title**: Display title for the link
- **description**: Description of what this link provides

### User Preferences (from Planning Service)
- **preferred_venue_types**: Favorite venue categories
- **preferred_price_range**: Budget preferences ($, $$, $$$)
- **preferred_amenities**: Desired features (wifi, outdoor_seating, etc.)
- **preferred_cities**: Favorite locations
- **min_rating**: Minimum acceptable rating
- **dietary_restrictions**: Food requirements (vegetarian, vegan, gluten-free, etc.)
- **accessibility_needs**: Accessibility requirements
- **activity_level**: Preferred activity intensity (low, medium, high)
- **group_size**: Typical group size for outings
- **special_interests**: Hobbies and interests

### Search Criteria
- query, location, radius_km, venue_types, min_rating, max_price, amenities, open_now, limit, offset

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google Places API**:
   - Get a Google Places API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Places API service
   - Set your API key in `app/services/place_finder.py`:
   ```python
   GOOGLE_API_KEY = "your_api_key_here"
   ```

4. **Configure MongoDB (for Ontopo caching)**:
   - The service uses MongoDB to cache Ontopo reservation links
   - Update the connection string in `app/services/ontopo_scraper.py` if needed
   - Default: Uses MongoDB Atlas cloud database

5. **Install ChromeDriver (for Ontopo scraping)**:
   - Download ChromeDriver from [ChromeDriver Downloads](https://chromedriver.chromium.org/)
   - Place `chromedriver.exe` in the service root directory
   - Ensure Chrome browser is installed on the system

6. Run the service:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🧠 **Personalization Algorithm**

The service uses a sophisticated weighted scoring system to personalize venue recommendations:

### **Scoring Weights**
- **Venue Type**: 25% - Matches preferred venue types (restaurant, cafe, museum, etc.)
- **Price Range**: 20% - Compatibility with budget preferences ($, $$, $$$)
- **Amenities**: 15% - Percentage of preferred amenities available
- **Rating**: 15% - How well venue rating meets minimum requirements
- **Location**: 15% - City preference matching
- **Dietary**: 10% - Accommodation of dietary restrictions

### **Scoring Logic**
- **Perfect Match**: 1.0 (exact preference match)
- **Close Match**: 0.7 (within acceptable range)
- **Partial Match**: 0.3-0.6 (some compatibility)
- **No Match**: 0.0 (incompatible)

### **Personalization Features**
- **User Preference Integration**: Fetches preferences from Outing-Profile-Service
- **Smart Ranking**: Venues automatically sorted by personalization score
- **Flexible Matching**: Handles missing preferences gracefully
- **Real-time Scoring**: Calculated on-demand for each search

## 🌐 **Google Places API Integration**

The service integrates with Google Places API to provide real-time venue discovery during plan generation:

### **How It Works**
1. **Plan Request**: User requests venues for specific types (restaurant, museum, etc.)
2. **Location Search**: Uses coordinates and radius to search Google Places API
3. **Venue Discovery**: Finds real venues with ratings, prices, and amenities
4. **Data Conversion**: Converts Google Places data to internal Venue objects
5. **Personalization**: Applies user preferences to rank discovered venues
6. **Plan Generation**: Creates comprehensive outing plan with real venue data

### **Venue Type Mapping**
- **restaurant** → Google Places "restaurant"
- **cafe** → Google Places "cafe"
- **bar** → Google Places "bar"
- **museum** → Google Places "museum"
- **theater** → Google Places "movie_theater"
- **park** → Google Places "park"
- **shopping_center** → Google Places "shopping_mall"
- **sports_facility** → Google Places "gym"
- **hotel** → Google Places "lodging"

### **Data Extraction**
- **Location**: Coordinates, address, city extraction
- **Rating**: User ratings from Google
- **Price Level**: Converted to $, $$, $$$ format
- **Amenities**: Extracted from place types (wheelchair accessible, parking, wifi, etc.)
- **Links**: Official websites when available

### **Benefits**
- **Real-time Data**: Always up-to-date venue information
- **Rich Details**: Ratings, prices, amenities from Google
- **Global Coverage**: Works worldwide with Google's extensive database
- **Automatic Updates**: No need to manually maintain venue database

## 🍽️ **Ontopo Integration for Food Venues**

The service automatically adds reservation links for restaurants and cafes using the Ontopo platform:

### **How It Works**
1. **Venue Discovery**: When a restaurant or cafe is found via Google Places API
2. **Automatic Scraping**: Ontopo scraper searches for the venue on Ontopo.com
3. **Reservation Link**: Extracts the direct reservation link for the venue
4. **Caching**: Stores discovered links in MongoDB for future use
5. **Link Attachment**: Automatically adds reservation links to venue objects

### **Supported Venue Types**
- **Restaurants**: Automatic reservation link discovery
- **Cafes**: Automatic reservation link discovery
- **Other Venues**: No automatic reservation links (only official websites if available)

### **Link Types Added**
- **Official Website**: From Google Places API (when available)
- **Reservation Link**: From Ontopo scraper (restaurants & cafes only)
- **Booking Type**: Marked as "booking" for easy identification

### **Benefits**
- **Seamless Booking**: Users can book tables directly from venue suggestions
- **Israeli Market Focus**: Optimized for Israeli restaurant booking via Ontopo
- **Smart Caching**: Avoids re-scraping for previously discovered venues
- **Automatic Discovery**: No manual work needed to add booking links

## Data Persistence

The service currently uses JSON-based file storage for data persistence. Data is automatically saved to the `data/` directory:
- `data/venues.json` - Venue data including links

## Future Enhancements

- Database integration (PostgreSQL, MongoDB)
- Authentication and authorization
- Image upload and storage
- Real-time notifications
- Advanced analytics and reporting
- Integration with external APIs (Google Places, Yelp, etc.)
- Link validation and health checking
- Automated link discovery and scraping
- **Machine learning** for preference learning
- **Collaborative filtering** for group recommendations
- **Real-time preference updates** from Planning Service

## Development

The service is built with:
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **Python 3.8+**: Modern Python features
- **httpx**: Async HTTP client for service integration
- **requests**: HTTP client for Google Places API integration
- **pymongo**: MongoDB client for caching Ontopo links
- **selenium**: Web scraping for Ontopo reservation links
- **ChromeDriver**: Browser automation for web scraping

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Planning Service Integration

The Venues Service integrates with the **Planning Service** to provide personalized recommendations:

- **Fetches user preferences** from the Planning Service
- **Scores venues** based on preference matching
- **Provides personalized rankings** for search results
- **Supports dietary restrictions** and accessibility needs
- **Considers activity levels** and group sizes

### Planning Service Configuration

Set the Planning Service URL (default: `http://localhost:8001`):
```python
# In app/services/planning_integration.py
planning_service_url = "http://localhost:8001"
```

## API Documentation

Once the service is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## Example Usage

### Create a Venue with Links
```bash
curl -X POST "http://localhost:8000/api/v1/venues" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Central Park Cafe",
    "description": "A cozy cafe in the heart of the city",
    "venue_type": "cafe",
    "location": {
      "latitude": 40.7589,
      "longitude": -73.9851,
      "address": "123 Central Park West",
      "city": "New York",
      "country": "USA"
    },
    "price_range": "$$",
    "amenities": ["wifi", "outdoor_seating", "coffee"],
    "links": [
      {
        "type": "website",
        "url": "https://centralparkcafe.com",
        "title": "Official Website",
        "description": "Main website with menu and hours"
      },
      {
        "type": "social_media",
        "url": "https://instagram.com/centralparkcafe",
        "title": "Instagram",
        "description": "Follow us for daily specials and photos"
      }
    ]
  }'
```

### Personalized Search (NEW!)
```bash
curl -X POST "http://localhost:8000/api/v1/search/personalized" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "location": {
      "latitude": 40.7589,
      "longitude": -73.9851
    },
    "radius_km": 5.0,
    "use_preferences": true,
    "limit": 10
  }'
```

### Get Personalized Recommendations (NEW!)
```bash
curl "http://localhost:8000/api/v1/recommendations/user123?limit=5"
```

### Add a Link to an Existing Venue
```bash
curl -X POST "http://localhost:8000/api/v1/venues/{venue_id}/links" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "booking",
    "url": "https://opentable.com/central-park-cafe",
    "title": "Make a Reservation",
    "description": "Book your table online"
  }'
```

### Search for Venues
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "latitude": 40.7589,
      "longitude": -73.9851
    },
    "radius_km": 5.0,
    "venue_types": ["cafe", "restaurant"],
    "min_rating": 4.0
  }'
```

### Get Venues by Type
```bash
curl "http://localhost:8000/api/v1/venues?venue_type=cafe&city=New%20York"
```

### Get All Links for a Venue
```
```