import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot.jaka_robot import JakaRobot
from integrations.voice_control import VoiceControl

def handle_robot_commands(robot, command):
    command = command.lower()  # Convert the command to lowercase to make the search case-insensitive
    if "power on" in command:
        robot.power_on()
        print("Robot powered on")
    # Add more command handling as needed

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
