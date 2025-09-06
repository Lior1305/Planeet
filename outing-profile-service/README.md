# 📋 Outing Profile Service

Manages user outing history, ratings, and profile data for completed outings.

## 🎯 Purpose

The Outing Profile Service tracks user outing history, handles venue ratings, and manages outing status updates for completed plans.

## 🛠️ Tech Stack

- **Language**: Python
- **Framework**: FastAPI
- **Database**: MongoDB
- **Container**: Docker

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python src/main.py
```

## 📡 API Endpoints

- `GET /outings/{user_id}` - Get user's outing history
- `POST /outings` - Add new outing to history
- `PUT /outings/{outing_id}/status` - Update outing status
- `POST /outings/{outing_id}/ratings` - Submit venue ratings
- `DELETE /outings/{outing_id}` - Remove outing from history

## 🗄️ Database Schema

- **Outings Collection**: Stores completed outing details
- **Ratings Collection**: User ratings for venues
- **Status Updates**: Outing status changes and timestamps

## 🔗 Dependencies

- **Planning Service**: Receives completed outing data
- **UI Service**: Provides outing history and rating interface
- **Venues Service**: Venue data for rating context

## 📝 Key Features

- Outing history tracking
- Venue rating system (1-5 stars)
- Status management (planned, completed, cancelled)
- User preference learning from ratings
- Outing analytics and insights

## 📊 Data Flow

1. **Outing Completion**: Planning Service → Outing Profile Service
2. **History Display**: UI Service ← Outing Profile Service
3. **Rating Submission**: UI Service → Outing Profile Service
4. **Preference Updates**: Outing Profile Service → Planning Service
