import sys
import os

# Add the parent directory to the sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot.jaka_robot import JakaRobot
from integrations.AIvision_integration import AIVisionIntegration

# Constants
PI = 3.1415926
ABSOLUTE_MODE = 0
JOINT_POSITIONS = [
    [PI / 20, PI / 17, PI / 130, PI / 4, 0, 0],
    [1, 0.6, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1.5, 1, 1, 1, 1],
]

# Helper function for movement
def move_robot(robot, position):
    robot.joint_move(joint_pos=position, move_mode=ABSOLUTE_MODE, is_block=True, speed=robot.speed)

def move_robot_to_positions(robot, ai_vision):
    for i in range(50):  # Loop for 50 iterations
        ret, frame = ai_vision.cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Check for persons in the frame
        person_detected, _ = ai_vision.detect_person(frame)

        # Move the robot to each position based on the iteration
        move_robot(robot, JOINT_POSITIONS[i % 4])

        # Adjust speed immediately after each movement
        robot.control_speed(person_detected)

def initialize_robot(ip_address):
    robot = JakaRobot(ip=ip_address)
    robot.login()
    robot.power_on()
    robot.enable_robot()
    return robot

def main():
    try:
        robot = initialize_robot(ip_address="192.168.0.124")
        ai_vision = AIVisionIntegration()

        # Run move_robot_to_positions after camera processing
        move_robot_to_positions(robot, ai_vision)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure resources are cleaned up
        ai_vision.cleanup()
        robot.logout()

if __name__ == "__main__":
    main()
