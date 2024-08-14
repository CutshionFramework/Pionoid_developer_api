import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot.jaka_robot import JakaRobot
from integrations.voice_control import VoiceControl

def handle_robot_commands(robot, command):
    command = command.lower()  # Convert the command to lowercase to make the search case-insensitive
    
    # Command map to organize commands and their corresponding actions
    command_map = {
        "power on": robot.power_on,
        "enable": robot.enable_robot,
        "get position": robot.get_joint_position,
        "start": lambda: robot.joint_move(joint_pos=[1, 0, 0, 0, 0, 0], move_mode=0, is_block=1, speed=robot.speed),  # Example position and move mode
    }
    
    # Iterate through the command map to find and execute the appropriate action
    for key, action in command_map.items():
        if key in command:
            result = action()  # Execute the action and store the result
            print(f"Executed command: {key}")
            if isinstance(result, tuple):  # If the result is a tuple, handle it appropriately
                if result[0] == 0:
                    print(f"The result of '{key}' is:", result[1])
                else:
                    print(f"Something happened during '{key}', the error code is:", result[0])
            elif result is not None:  # Print the result if it is not None and not a tuple
                print(f"Output: {result}")
            return

    print(f"Unrecognized command: {command}")

if __name__ == "__main__":
    robot = JakaRobot("192.168.0.124")
    robot.login()
    
    voice_control = VoiceControl()
    while True:
        command = voice_control.recognize_speech()  # Recognize speech and get the command as text
        if command:
            doc = voice_control.process_command(command)  # Process the command text with Spacy
            handle_robot_commands(robot, command)  # Handle the robot's response to the command
            print(f"Processed command: {doc}")
