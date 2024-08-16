import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot.jaka_robot import JakaRobot
from integrations.mongodb_storage import MongoDBStorage

def handle_robot_commands(robot, command, storage):
    command = command.lower()
    
    command_map = {
        "power on": robot.power_on,
        "enable": robot.enable_robot,
        "get position": robot.get_joint_position,
        "start": lambda: robot.joint_move(joint_pos=[1, 0, 0, 0, 0, 0], move_mode=0, is_block=1, speed=robot.speed),
    }
    
    for key, action in command_map.items():
        if key in command:
            start_time = datetime.now(timezone.utc)
            result = action()
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()

            # For movement commands, store the movement details
            if key == "start":
                # Retrieve the position after the move to store
                position_result = robot.get_joint_position()
                if isinstance(position_result, tuple) and len(position_result) > 1:
                    position = position_result[1]
                    storage.store_movement(command, position, duration)

            # Print the result directly
            if isinstance(result, tuple):
                if len(result) > 1:
                    print(result[1])  # Print the position or other data if available
                else:
                    print(f"Command '{key}' executed successfully.")
            elif result is not None:
                print(result)
            else:
                print(f"Command '{key}' executed with no return value.")
            return

    print(f"Unrecognized command: {command}")

if __name__ == "__main__":
    robot = JakaRobot("192.168.0.109")
    robot.login()
    
    storage = MongoDBStorage()  # Initialize MongoDB storage with default settings

    try:
        while True:
            command = input("Enter command: ")
            if command:
                handle_robot_commands(robot, command, storage)
    finally:
        storage.close()  # Ensure the MongoDB connection is closed
