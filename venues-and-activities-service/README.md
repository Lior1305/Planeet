# 🏢 Venues & Activities Service

Discovers and manages venue data, providing real-time information and recommendations.

## 🎯 Purpose

The Venues Service is responsible for venue discovery, data management, and providing venue information to other services for planning and booking.

## 🛠️ Tech Stack

- **Language**: Python
- **Framework**: FastAPI
- **Database**: MongoDB
- **Web Scraping**: Selenium, BeautifulSoup
- **Container**: Docker

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python run.py
```

## 📡 API Endpoints

- `GET /venues` - Get venues with filters
- `GET /venues/{venue_id}` - Get specific venue details
- `POST /venues/search` - Search venues by criteria
- `GET /venues/types` - Get available venue types
- `POST /venues/discover` - Trigger venue discovery

## 🗄️ Database Schema

- **Venues Collection**: Complete venue information
- **Types Collection**: Venue categories and types
- **Reviews Collection**: Venue ratings and reviews
- **Availability Collection**: Real-time venue status

## 🔗 Dependencies

- **Planning Service**: Provides venue recommendations
- **Booking Service**: Supplies venue data for reservations
- **UI Service**: Displays venue information

## 📝 Key Features

- **Venue Discovery**: Automated web scraping for new venues
- **Real-time Data**: Live availability and status updates
- **Smart Search**: Advanced filtering and recommendation
- **Data Enrichment**: Reviews, ratings, and detailed information
- **Location Services**: Geographic search and proximity matching
