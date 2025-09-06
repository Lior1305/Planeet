# 👥 Users Service

Manages user authentication, registration, and profile management.

## 🎯 Purpose

The Users Service handles all user-related operations including registration, login, profile updates, and user data management.

## 🛠️ Tech Stack

- **Language**: Java
- **Framework**: Spring Boot
- **Database**: PostgreSQL
- **Build Tool**: Maven

## 🚀 Quick Start

```bash
# Build the project
./mvnw clean package

# Run the service
./mvnw spring-boot:run
```

## 📡 API Endpoints

- `POST /users` - Register new user
- `GET /users` - Get all users (for login)
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user profile
- `DELETE /users/{id}` - Delete user account

## 🗄️ Database Schema

- **Users Table**: Stores user credentials, profile info, and preferences
- **Fields**: id, username, email, password, phone, created_at, updated_at

## 🔗 Dependencies

- **UI Service**: Receives user registration and login requests
- **Planning Service**: Provides user data for outing planning
- **Notification Service**: User data for invitation management

## 📝 Key Features

- User registration with validation
- Secure login authentication
- Profile management and updates
- Email uniqueness validation
- Username availability checking

