import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core_robot import core_robot
from UR_robot import URRobot
from jaka_robot import JakaRobot


#now write code that can work with any robot
def initialize_robot(robot: core_robot):
    robot.login()
    robot.power_on()
    robot.enable_robot()

def move_robot(robot: core_robot, joint_positions, tcp_position):
    robot.joint_move(joint_pos=joint_positions, move_mode=0, is_block=True, speed=1.0)
    robot.linear_move(tcp_pos=tcp_position, move_mode=0, is_block=True, speed=1.0)

def print_robot_status(robot: core_robot):
    state = robot.get_robot_state()
    tcp_pos = robot.get_tcp_position()
    print("Robot state:", state)
    print("TCP position:", tcp_pos)

if __name__ == "__main__":
    # Example with URRobot
    ur_robot = URRobot("192.168.88.129")
    initialize_robot(ur_robot)
    move_robot(ur_robot, [0.0, -1.57, 0.0, -1.57, 0.0, 0.0], [0.5, 0.5, 0.5, 0, 0, 0])
    print_robot_status(ur_robot)
    ur_robot.logout()

    # Example with JakaRobot
    jaka_robot = JakaRobot("192.168.0.130")
    initialize_robot(jaka_robot)
    move_robot(jaka_robot, [0.0, -1.57, 0.0, -1.57, 0.0, 0.0], [0.5, 0.5, 0.5, 0, 0, 0])
    print_robot_status(jaka_robot)
    jaka_robot.logout()