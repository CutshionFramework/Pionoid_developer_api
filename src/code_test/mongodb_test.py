import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from robot.core_robot import core_robot
from robot.custom_robots.jaka_robot import JakaRobot

from integrations.mongodb_storage import MongoDBStorage

def initialize_robot(robot: core_robot):
    robot.login()
    robot.power_on()
    robot.enable_robot()

def joint_move_robot(robot: core_robot, joint_positions):
    robot.joint_move(joint_pos=joint_positions, move_mode=0, is_block=True, speed=1.0)

def get_joint_position(robot: core_robot):
    status = robot.get_joint_position()
    return status

# Example usage
if __name__ == "__main__":
    storage = MongoDBStorage()

    # Example with JakaRobot
    jaka_robot = JakaRobot("192.168.0.116")
    initialize_robot(jaka_robot)
    joint_move_robot(jaka_robot, [0.0, 1.57, -1.0, 0.0, 0.0, 0.0])
    
    joint_position = jaka_robot.get_joint_position()

    print(joint_position[1])

    
    jaka_robot.logout()

    # 1. data insert
    inserted_id = storage.store_movement(
        command="joint_move", 
        position={"joint_position" : joint_position[1]}, 
        duration=5.0
    )
    print(f"Inserted document ID: {inserted_id}")

    # 2. data update
    updated_count = storage.update_movement(
        movement_id=inserted_id, 
        updated_data={"command": "linear_move"}
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