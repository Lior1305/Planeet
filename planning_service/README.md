# Planning Service

A FastAPI service that orchestrates outing planning by integrating with the **Outing-Profile-Service** for user preferences and the **Venues Service** to create comprehensive venue plans based on user requirements.

## 🎯 **Service Flow**

```
User Input → Planning Service → Outing-Profile-Service (preferences) → Venues Service → Planning Service → Booking Service + UI
```

### **1. User Input**
- User provides outing requirements (venue types, location, date, time, group size, budget)
- Planning Service receives and validates the input

### **2. Preference Retrieval**
- Planning Service fetches user preferences from **Outing-Profile-Service**
- User preferences include venue types, price ranges, amenities, dietary restrictions, etc.

### **3. Plan Generation**
- Planning Service sends plan request to Venues Service (including user preferences)
- Venues Service discovers venues, applies personalization, and generates comprehensive plan
- Plan includes venue suggestions, costs, durations, travel routes, and links

### **4. Plan Delivery**
- Venues Service returns complete plan to Planning Service
- Planning Service stores plan and sends to Booking Service and UI
- User receives complete outing plan with all venue details and links

## 🏗️ **Architecture**

### **Planning Service (Orchestrator)**
- **Port**: 8001
- **Role**: Receives user input, coordinates with other services, manages plan lifecycle
- **Endpoints**: Plan creation, retrieval, status updates

### **Outing-Profile-Service (User Data)**
- **Port**: 8002
- **Role**: Stores and manages user preferences, profiles, and outing history
- **Data**: User preferences, dietary restrictions, accessibility needs, favorite venues

### **Venues Service (Venue Discovery)**
- **Port**: 8000
- **Role**: Discovers venues, applies personalization, generates comprehensive plans
- **Endpoints**: Plan generation, venue search, personalization

## 📡 **API Endpoints**

### **Plan Management**
- `POST /v1/plans/create` - Create new outing plan
- `GET /v1/plans/{plan_id}` - Get specific plan
- `GET /v1/plans` - Get user's plans
- `POST /v1/plans/{plan_id}/status` - Update plan status
- `POST /v1/plans/{plan_id}/notify` - Receive plan notifications
- `POST /v1/plans/{plan_id}/response` - Receive plan response from Venues Service

### **User Preferences (from Outing-Profile-Service)**
- `GET /v1/outing-preferences` - Get user preferences from Outing-Profile-Service
- `GET /v1/outing-profile` - Get user profile from Outing-Profile-Service

### **Health & Status**
- `GET /v1/health` - Service health check

## 🔄 **Integration Flow**

### **1. Plan Creation Request**
```json
{
  "user_id": "user123",
  "venue_types": ["restaurant", "museum"],
  "location": {
    "latitude": 40.7589,
    "longitude": -73.9851,
    "city": "New York"
  },
  "date": "2024-01-15T18:00:00",
  "group_size": 4,
  "budget_range": "$$",
  "use_personalization": true,
  "max_venues": 3
}
```

### **2. Preference Retrieval**
Planning Service fetches user preferences from Outing-Profile-Service:
```json
{
  "user_id": "user123",
  "preferred_venue_types": ["restaurant", "cafe", "museum"],
  "preferred_price_range": "$$",
  "preferred_amenities": ["wifi", "outdoor_seating"],
  "dietary_restrictions": ["vegetarian"],
  "accessibility_needs": ["wheelchair_accessible"]
}
```

### **3. Venues Service Response**
```json
{
  "plan_id": "plan_uuid",
  "user_id": "user123",
  "suggested_venues": [
    {
      "venue_id": "venue1",
      "name": "Central Park Restaurant",
      "venue_type": "restaurant",
      "rating": 4.5,
      "price_range": "$$",
      "personalization_score": 0.92,
      "links": [
        {
          "type": "website",
          "url": "https://centralparkrestaurant.com",
          "title": "Official Website"
        },
        {
          "type": "booking",
          "url": "https://opentable.com/central-park",
          "title": "Make Reservation"
        }
      ]
    }
  ],
  "estimated_total_duration": 4.5,
  "travel_route": [...],
  "personalization_applied": true,
  "average_personalization_score": 0.85
}
```

## 🚀 **Getting Started**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run the Service**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### **3. Service Configuration**
Set service URLs in the respective client files:

**Outing-Profile-Service URL** (in `app/services/outing_profile_client.py`):
```python
outing_profile_service_url = "http://localhost:8002"  # Default
```

**Venues Service URL** (in `app/services/venues_service_client.py`):
```python
venues_service_url = "http://localhost:8000"  # Default
```

## 🔧 **Configuration**

### **Environment Variables**
- `OUTING_PROFILE_SERVICE_URL`: URL of the Outing-Profile-Service (default: http://localhost:8002)
- `VENUES_SERVICE_URL`: URL of the Venues Service (default: http://localhost:8000)
- `PLANNING_SERVICE_PORT`: Port for Planning Service (default: 8001)

### **Service URLs**
- **Planning Service**: http://localhost:8001
- **Outing-Profile-Service**: http://localhost:8002
- **Venues Service**: http://localhost:8000
- **API Documentation**: http://localhost:8001/docs

## 📊 **Plan Lifecycle**

1. **Created**: Plan request received and sent to Venues Service
2. **Processing**: Venues Service is generating the plan
3. **Completed**: Plan generated successfully with venue suggestions
4. **Failed**: Plan generation failed (error details provided)

## 🔗 **Service Communication**

### **Planning Service → Outing-Profile-Service**
- User preference retrieval
- User profile retrieval

### **Planning Service → Venues Service**
- Plan generation requests
- Venue search queries
- Venue detail requests

### **Venues Service → Planning Service**
- Plan responses with venue suggestions
- Status updates during generation
- Completion notifications

## 🎨 **Example Usage**

### **Create a New Plan**
```bash
curl -X POST "http://localhost:8001/v1/plans/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "venue_types": ["restaurant", "museum"],
    "location": {
      "latitude": 40.7589,
      "longitude": -73.9851,
      "city": "New York"
    },
    "date": "2024-01-15T18:00:00",
    "group_size": 4,
    "budget_range": "$$",
    "use_personalization": true,
    "max_venues": 3
  }'
```

### **Get Plan Details**
```bash
curl "http://localhost:8001/v1/plans/{plan_id}"
```

### **Get User Plans**
```bash
curl "http://localhost:8001/v1/plans?user_id=user123"
```

### **Get User Preferences (from Outing-Profile-Service)**
```bash
curl "http://localhost:8001/v1/outing-preferences?user_id=user123"
```

## 🚧 **Future Enhancements**

- **Database Integration**: Replace in-memory storage with PostgreSQL/MongoDB
- **Booking Service Integration**: Send plans to booking service for reservations
- **Real-time Updates**: WebSocket notifications for plan status changes
- **Plan Templates**: Pre-defined plan templates for common outing types
- **Collaborative Planning**: Group planning features
- **Plan Optimization**: AI-powered venue sequencing and timing optimization

## 🐛 **Troubleshooting**

### **Common Issues**
1. **Outing-Profile-Service Unreachable**: Check if service is running on port 8002
2. **Venues Service Unreachable**: Check if service is running on port 8000
3. **Plan Generation Timeout**: Increase timeout in venues service client
4. **Missing Dependencies**: Ensure httpx is installed

### **Logs**
Check service logs for detailed error information:
```bash
# Planning Service logs
uvicorn app.main:app --log-level debug

# Outing-Profile-Service logs
# Check your Outing-Profile-Service logs

# Venues Service logs  
uvicorn app.main:app --log-level debug
```

## 📝 **Development**

### **Project Structure**
```
planning_service/
├── app/
│   ├── api/
│   │   └── routes.py                    # API endpoints
│   ├── models/
│   │   └── plan_request.py              # Data models
│   ├── services/
│   │   ├── venues_service_client.py     # Venues Service integration
│   │   └── outing_profile_client.py     # Outing-Profile-Service integration
│   └── main.py                          # FastAPI application
├── requirements.txt                      # Dependencies
└── README.md                            # This file
```

### **Adding New Features**
1. Create models in `app/models/`
2. Add business logic in `app/services/`
3. Create endpoints in `app/api/routes.py`
4. Update tests and documentation

## 📄 **License**

This project is licensed under the MIT License.
