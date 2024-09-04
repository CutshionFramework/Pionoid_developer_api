import pymongo
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")

class MongoDBStorage:
    def __init__(self, db_name="Pionoidrobotics", collection_name="movements", uri=mongodb_uri):
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
    
    def update_movement(self, movement_id, updated_data):
        # Update a movement by its _id
        result = self.collection.update_one(
            {"_id": movement_id}, 
            {"$set": updated_data}
        )
        return result.modified_count  # Return the number of documents modified

    def delete_movement(self, movement_id):
        # Delete a movement by its _id
        result = self.collection.delete_one({"_id": movement_id})
        return result.deleted_count  # Return the number of documents deleted

    def find_movements_by_command(self, command, limit=10):
        # Retrieve movements by command, sorted by timestamp
        return list(self.collection.find({"command": command}).sort("timestamp", pymongo.DESCENDING).limit(limit))

    def close(self):
        # Close the MongoDB connection
        self.client.close()

    # Optional: Additional methods for filtering or deleting movements can be added here

# Example usage
if __name__ == "__main__":
    # MongoDBStorage 클래스 인스턴스 생성
    storage = MongoDBStorage()

    # 1. data insert
    inserted_id = storage.store_movement(
        command="move_forward", 
        position={"x": 10, "y": 20, "z": 30}, 
        duration=5.0
    )
    print(f"Inserted document ID: {inserted_id}")

    # 2. data update
    updated_count = storage.update_movement(
        movement_id=inserted_id, 
        updated_data={"command": "move_backward"}
    )
    print(f"Number of documents updated: {updated_count}")

    # 3. data find (filtering)
    movements = storage.find_movements_by_command(command="move_backward", limit=5)
    for movement in movements:
        print(movement)

    # 4. data delete
    # deleted_count = storage.delete_movement(movement_id=inserted_id)
    # print(f"Number of documents deleted: {deleted_count}")

    # 5. 연결 종료
    storage.close()
