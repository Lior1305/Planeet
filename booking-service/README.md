# 🎫 Booking Service

Handles venue reservations and booking confirmations for planned outings.

## 🎯 Purpose

The Booking Service manages the reservation process for venues selected in outing plans, providing real-time booking status and confirmation details.

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
python app/main.py
```

## 📡 API Endpoints

- `POST /bookings` - Create new venue bookings
- `GET /bookings/{booking_id}` - Get booking details
- `PUT /bookings/{booking_id}/status` - Update booking status
- `DELETE /bookings/{booking_id}` - Cancel booking

## 🗄️ Database Schema

- **Bookings Collection**: Stores booking details, status, and venue information
- **Venues Collection**: Cached venue data for quick access

## 🔗 Dependencies

- **Venues Service**: Fetches venue details and availability
- **Planning Service**: Receives booking requests from planned outings
- **Users Service**: Validates user permissions

## 📝 Key Features

- Real-time booking status updates
- Venue availability checking
- Booking confirmation management
- Error handling and retry logic
