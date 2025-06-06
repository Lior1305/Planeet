import os
import logging
from flask import Flask, jsonify, request
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB connection
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client.outing_profiles
profiles_collection = db.profiles

@app.route('/')
def home():
    logger.info("Home endpoint was hit")
    return jsonify({"message": "Welcome to Outing Profile Server"})

@app.route('/profiles', methods=['POST'])
def add_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        name = data.get("name")

        logger.info(f"Attempting to add profile: {data}")

        if not user_id or not name:
            logger.warning("Missing user_id or name in request")
            return jsonify({"error": "user_id and name are required"}), 400

        profile = {"user_id": user_id, "name": name}
        profiles_collection.insert_one(profile)

        logger.info(f"Profile added: {profile}")
        return jsonify({"message": "Profile added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding profile: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/profiles', methods=['GET'])
def get_profiles():
    try:
        profiles = list(profiles_collection.find({}, {"_id": 0}))
        logger.info(f"Retrieved {len(profiles)} profiles")
        return jsonify(profiles), 200
    except Exception as e:
        logger.error(f"Error retrieving profiles: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Outing Profile Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
