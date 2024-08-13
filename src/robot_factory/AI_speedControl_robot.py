import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot.jaka_robot import JakaRobot

from integrations.AIvision_integration import AIVisionIntegration

# Constants
PI = 3.1415926
ABS = 0
joint_positions1 = [PI/20, PI/17, PI/130, PI/4, 0, 0]
joint_positions2 = [1, 0.6, 1, 1, 1, 1]
joint_positions3 = [1, 1, 1, 1, 1, 1]
joint_positions4 = [1, 1.5, 1, 1, 1, 1]

# custom robot child project
def move_robot_to_positions(robot, ai_vision):
    for i in range(50):  # Loop for 50 rounds
        ret, frame = ai_vision.cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Check for persons in the frame
        person_detected, _ = ai_vision.detect_person(frame)

        # Move the robot to each position
        if i % 4 == 0:
            robot.joint_move(joint_pos=joint_positions1, move_mode=ABS, is_block=True, speed=robot.speed)
        elif i % 4 == 1:
            robot.joint_move(joint_pos=joint_positions2, move_mode=ABS, is_block=True, speed=robot.speed)
        elif i % 4 == 2:
            robot.joint_move(joint_pos=joint_positions3, move_mode=ABS, is_block=True, speed=robot.speed)
        else:
            robot.joint_move(joint_pos=joint_positions4, move_mode=ABS, is_block=True, speed=robot.speed)

        # Adjust speed immediately after each movement
        robot.control_speed(person_detected)

def main():
    robot = JakaRobot(ip="192.168.0.220")

    robot.login()
    robot.power_on()
    robot.enable_robot()

    ai_vision = AIVisionIntegration()

    # Run move_robot_to_positions after camera processing
    move_robot_to_positions(robot, ai_vision)

    # Cleanup
    ai_vision.cleanup()
    robot.logout()

if __name__ == "__main__":
    main()