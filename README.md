# 🌟 Planeet - Plan Together, Fast!

> *Because deciding where to go shouldn't take longer than the actual outing!*

A microservices-based web application for group outing planning, built as part of our final year project.

## 🎯 What is Planeet?

Planeet helps groups plan outings without the endless "where should we go?" group chats. We've got a comprehensive venue database, real-time availability, and seamless friend invitations to make planning actually fun!

### ✨ Key Features

- 🎯 **Personalized Matching** - Find venues that match your group's vibe
- 📍 **Live Venue Data** - Real-time availability and status updates  
- 👥 **Invite Friends** - Seamless group planning with friend invitations
- 💬 **Decide Together** - Share options and vote in seconds
- ❤️ **Save Favorites** - Build your personal collection of go-to spots
- 📱 **Mobile-First** - Works perfectly on all devices

## 🏗️ Architecture

Built with a modern microservices architecture:

- **UI Service** (React) - Frontend interface
- **Planning Service** (Python) - Core planning logic
- **Users Service** (Java) - User management
- **Venues Service** (Python) - Venue discovery and data
- **Booking Service** (Python) - Reservation handling
- **Outing Profile Service** (Python) - User outing history

## 🛠️ Tech Stack

- **Frontend**: React, CSS3, React Router
- **Backend**: Python (FastAPI), Java (Spring Boot)
- **Databases**: MongoDB, PostgreSQL
- **Infrastructure**: Docker, Kubernetes, Azure
- **Deployment**: Azure Kubernetes Service

## 📚 Project Documentation

- 📋 **[Project Proposal](project-info/Project%20proposal.md)** - Initial project concept and requirements
- 🏗️ **[High Level Design](project-info/High%20Level%20Design.md)** - System architecture and design decisions

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 16+
- Java 11+
- Python 3.8+

### Running Locally

1. **Clone and start services**
   ```bash
   git clone <repository-url>
   cd Planeet
   docker-compose up -d
   ```

2. **Access the application**
   ```
   http://localhost:3000
   ```

## 🎯 How It Works

1. **Sign Up** - Create an account and set preferences
2. **Start Planning** - Choose location, date, and group size
3. **Get Recommendations** - System finds perfect venues
4. **Invite Friends** - Send invitations and let everyone vote
5. **Book & Go** - Confirm choices and enjoy!

## 🧪 Testing

The app includes comprehensive error handling and validation:

- **Registration**: Duplicate email detection, field validation
- **Login**: Username/password validation with specific error messages
- **Planning**: Real-time form validation
- **Mobile**: Responsive design with hamburger navigation

## 📱 Mobile Support

- Responsive design that works on all screen sizes
- Mobile-friendly navigation with hamburger menu
- Touch-optimized interface
- Real-time validation on mobile devices

## 🐛 Known Issues & Future Work

- Real-time notifications could be enhanced
- Payment integration for reservations
- Calendar integration
- Native mobile apps

## 👥 Team

- Lior Berlin
- Dar Toledano
- Nika Klimenchuk

Built as part of our final year project in the Academic Collage of Tel Aviv - Yaffo.

---

*"Because the best memories are made together"* 🎉