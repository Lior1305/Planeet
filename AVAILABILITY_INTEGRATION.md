# Availability Integration Documentation

## Overview

This document describes how the availability integration works between the Venues Service, Booking Service, and Planning Service to ensure only available venues are returned to users.

## Architecture Flow

```
Planning Service → Venues Service → Booking Service
     ↑                    ↓
     └── Only Available Venues ←
```

## How It Works

### 1. Planning Service Request
When a user requests a plan, the Planning Service sends a request to the Venues Service with:
- `venue_types`: List of venue types to search for
- `location`: Geographic location for the search
- `radius_km`: Search radius
- `requested_time`: Specific time for availability check (format: "HH:MM")
- `group_size`: Number of people in the group

### 2. Venues Service Discovery
The Venues Service:
1. **Discovers venues** from Google Places API (gets 10 venues per type)
2. **Generates time slots** for each venue by calling the Booking Service
3. **Filters venues by availability** using the Booking Service overlap checking
4. **Returns only available venues** to the Planning Service

### 3. Availability Filtering Process

#### Step 1: Time Slot Generation
For each discovered venue, the Venues Service calls:
```
POST /v1/generate-time-slots
{
  "venue_id": "venue_mongodb_id",
  "default_counter": 100
}
```

#### Step 2: Availability Checking
For each venue, the Venues Service checks availability by calling:
```
GET /v1/availability/google-place/{google_place_id}/overlapping/{time_slot}
```

The Booking Service:
- Finds overlapping time slots for the requested time
- Checks if there's enough capacity for the group size
- Returns availability status and capacity information

#### Step 3: Filtering Logic
The Venues Service filters venues based on:
- **Availability**: `available = true`
- **Capacity**: `counter >= group_size`

Only venues that meet both criteria are returned to the Planning Service.

## API Endpoints

### Venues Service
- `POST /api/v1/venues/discover` - Main discovery endpoint with availability filtering

### Booking Service
- `GET /v1/health` - Health check
- `POST /v1/generate-time-slots` - Generate time slots for a venue
- `GET /v1/availability/google-place/{id}/overlapping/{time_slot}` - Check availability

### Planning Service
- `POST /plans/create` - Create a plan (calls venues service internally)

## Configuration

### Environment Variables
- `BOOKING_SERVICE_URL`: URL of the booking service (default: "http://booking-service:8004")

### Service URLs (Development)
- Planning Service: `http://localhost:8001`
- Venues Service: `http://localhost:8002`
- Booking Service: `http://localhost:8004`

## Testing

Run the integration test:
```bash
python test_availability_integration.py
```

This test will:
1. Check if all services are healthy
2. Test the full integration flow
3. Verify that only available venues are returned

## Error Handling

### Venues Service
- If Booking Service is unavailable, venues are still returned (without availability filtering)
- Logs warnings for failed availability checks
- Continues processing even if some venues fail availability checks

### Booking Service
- Returns appropriate HTTP status codes
- Provides detailed error messages
- Handles invalid venue IDs gracefully

## Logging

The integration includes comprehensive logging:
- `🔍 Checking availability for X venues...`
- `✅ X venues available for {time} (group size: {size})`
- `❌ Venue not available: X slots < Y needed`
- `⚠️ Booking service connectivity test failed`

## Performance Considerations

- **Parallel Processing**: Venues are checked for availability in parallel
- **Timeout Handling**: 30-second timeout for availability checks
- **Caching**: Time slots are generated once and stored in MongoDB
- **Fallback**: If availability checking fails, venues are still returned

## Future Improvements

1. **Caching**: Cache availability results for better performance
2. **Batch Operations**: Check multiple venues in a single API call
3. **Real-time Updates**: WebSocket updates for availability changes
4. **Advanced Filtering**: Filter by price range, rating, etc.
5. **Load Balancing**: Distribute availability checks across multiple booking service instances
