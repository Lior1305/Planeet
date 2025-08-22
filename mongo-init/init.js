// MongoDB initialization script for Planeet database
// This script will be run when the MongoDB container starts

db = db.getSiblingDB('planeet');

// Create venues collection
db.createCollection('venues');

// Create time_slots collection
db.createCollection('time_slots');

// Create indexes for better performance
db.venues.createIndex({ "name": 1 });
db.venues.createIndex({ "venue_type": 1 });
db.venues.createIndex({ "location.city": 1 });
db.venues.createIndex({ "rating": -1 });

db.time_slots.createIndex({ "venue_id": 1 });
db.time_slots.createIndex({ "date": 1 });
db.time_slots.createIndex({ "start_time": 1 });

print('Planeet database initialized successfully!');
print('Collections created: venues, time_slots');
