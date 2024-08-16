import pymongo
from datetime import datetime, timezone

class MongoDBStorage:
    def __init__(self, db_name="Pionoidrobotics", collection_name="movements", uri="mongodb://localhost:27017/"):
        # Initialize the MongoDB client and select the database and collection
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def store_movement(self, command, position, duration):
        # Prepare the data to store
        data = {
            "command": command,
            "position": position,
            "duration": duration,
            "timestamp": datetime.now(timezone.utc)  # Current UTC time
        }
        # Insert the data into the MongoDB collection
        result = self.collection.insert_one(data)
        return result.inserted_id

    def get_movements(self, limit=10):
        # Retrieve a limited number of recent movements, sorted by timestamp
        return list(self.collection.find().sort("timestamp", pymongo.DESCENDING).limit(limit))

    def close(self):
        # Close the MongoDB connection
        self.client.close()

    # Optional: Additional methods for filtering or deleting movements can be added here
