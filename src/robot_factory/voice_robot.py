import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot.jaka_robot import JakaRobot
from integrations.voice_control import VoiceControl

def handle_robot_commands(robot, command):
    if "power on" in command:
        robot.power_on()
        print("Robot powered on")
    # Add more command handling as needed

if __name__ == "__main__":
    robot = JakaRobot("192.168.0.220")
    robot.login()
    
    voice_control = VoiceControl()
    while True:
        command = voice_control.recognize_speech()
        doc = voice_control.process_command(command)
        handle_robot_commands(robot, command)