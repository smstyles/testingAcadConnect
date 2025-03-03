import os
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from datetime import datetime

# Configuration class
class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/messaging_app")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize MongoDB
mongo = PyMongo(app)

# Define models
class User:
    @staticmethod
    def get_user_by_id(user_id):
        return mongo.db.users.find_one({"_id": user_id})

    @staticmethod
    def create_user(user_data):
        return mongo.db.users.insert_one(user_data)

class Message:
    @staticmethod
    def get_messages_between_users(user1_id, user2_id):
        return mongo.db.messages.find({
            "$or": [
                {"sender_id": user1_id, "receiver_id": user2_id},
                {"sender_id": user2_id, "receiver_id": user1_id}
            ]
        }).sort("timestamp")

    @staticmethod
    def create_message(message_data):
        return mongo.db.messages.insert_one(message_data)

# Define blueprint
main = Blueprint('main', __name__)

@main.route("/messages", methods=["GET"])
def get_messages():
    user1_id = request.args.get("user1_id")
    user2_id = request.args.get("user2_id")
    messages = Message.get_messages_between_users(user1_id, user2_id)
    return jsonify([message for message in messages])

@main.route("/messages", methods=["POST"])
def send_message():
    data = request.get_json()
    message_data = {
        "sender_id": data["sender_id"],
        "receiver_id": data["receiver_id"],
        "content": data["content"],
        "timestamp": datetime.utcnow()
    }
    result = Message.create_message(message_data)
    return jsonify({"inserted_id": str(result.inserted_id)}), 201

@main.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user_data = {
        "username": data["username"],
        "email": data["email"]
    }
    result = User.create_user(user_data)
    return jsonify({"inserted_id": str(result.inserted_id)}), 201

# Register blueprints
app.register_blueprint(main)

# Define a basic route
@app.route("/")
def home():
    return "Hello, Flask is running!"

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
