from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from robot.custom_robots.jaka_robot import JakaRobot

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def initialize_robot(robot):
    robot.login()
    robot.power_on()
    robot.enable_robot()

def move_robot(robot, joint_positions):
    robot.joint_move(joint_pos=joint_positions, move_mode=0, is_block=True, speed=1.0)

def print_robot_status(robot):
    state = robot.get_robot_state()
    tcp_pos = robot.get_tcp_position()
    print("Robot state:", state)
    print("TCP position:", tcp_pos)

@app.route('/api/handle-robot', methods=['POST'])
def handle_robot():
    try:
        robot = JakaRobot("192.168.0.111")
        initialize_robot(robot)
        move_robot(robot, [1, 0, 0, 0, 0, 0])
        print_robot_status(robot)
        robot.logout()
        return jsonify({'message': 'Robot operation successful'}), 200
    except Exception as error:
        print(f'Error handling robot operation: {error}')
        return jsonify({'message': 'Robot operation failed'}), 500

if __name__ == '__main__':
    app.run(port=5000)