# 🎯 Planning Service

Core service that orchestrates outing planning, venue discovery, and group coordination.

## 🎯 Purpose

The Planning Service is the brain of Planeet, handling plan creation, venue recommendations, group invitations, and coordination between all other services.

## 🛠️ Tech Stack

- **Language**: Python
- **Framework**: FastAPI
- **Dependencies**: Multiple service integrations
- **Container**: Docker

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app/main.py
```

## 📡 API Endpoints

- `POST /v1/plans/create` - Create new outing plan
- `GET /v1/plans/{plan_id}` - Get plan details
- `POST /v1/plans/{plan_id}/invite` - Invite participants
- `PUT /v1/plans/{plan_id}/respond` - Respond to invitation
- `GET /v1/countries` - Get available countries
- `GET /v1/cities` - Get available cities

## 🔗 Service Integrations

- **Venues Service**: Fetches venue recommendations
- **Users Service**: Validates user data and permissions
- **Booking Service**: Handles venue reservations
- **Outing Profile Service**: Saves completed outings
- **UI Service**: Provides planning interface

## 📝 Key Features

- **Smart Planning**: Personalized venue recommendations
- **Group Coordination**: Invitation and response management
- **Location Services**: Country and city selection
- **Preference Matching**: Based on user history and ratings
- **Real-time Updates**: Live plan status and participant responses

## 🧠 Planning Algorithm

1. **Input Processing**: Parse user preferences and constraints
2. **Venue Discovery**: Query venues based on location and criteria
3. **Personalization**: Apply user preferences and rating history
4. **Recommendation**: Generate ranked venue suggestions
5. **Group Management**: Handle invitations and responses

## 📊 Data Flow

1. **Plan Creation**: UI → Planning Service → Venues Service
2. **Recommendations**: Venues Service → Planning Service → UI
3. **Invitations**: Planning Service → Users Service → UI
4. **Completion**: Planning Service → Outing Profile Service