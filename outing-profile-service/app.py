import os
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection - simple connection with default values
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client.outing_profiles  # Use the database
profiles_collection = db.profiles # Collection for profiles

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Outing Profile Server"})

# Route to add a new profile
@app.route('/profiles', methods=['POST'])
def add_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        name = data.get("name")

        if not user_id or not name:
            return jsonify({"error": "user_id and name are required"}), 400

        # Create a profile document
        profile = {"user_id": user_id, "name": name}
        profiles_collection.insert_one(profile)

        return jsonify({"message": "Profile added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get all profiles
@app.route('/profiles', methods=['GET'])
def get_profiles():
    try:
        profiles = list(profiles_collection.find({}, {"_id": 0}))  # Exclude MongoDB's internal _id field
        return jsonify(profiles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)