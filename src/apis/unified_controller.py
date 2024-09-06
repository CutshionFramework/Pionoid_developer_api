from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import sys
import os
from dotenv import load_dotenv
import redis
import pickle

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from robot.core_robot import core_robot
from robot.custom_robots.UR_robot import URRobot
from robot.custom_robots.jaka_robot import JakaRobot

app = Flask(__name__)
CORS(app)  # Enable CORS

# Get the secret key from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize Redis using environment variables
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 0))
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

# Mapping of robot types to their corresponding subclasses
ROBOT_SUBCLASSES = {
    'URRobot': URRobot,
    'JakaRobot': JakaRobot
}

### Utility functions

# Token generation function
def generate_token(ip, robot_type):
    token = jwt.encode({
        'ip': ip,
        'robot_type': robot_type
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# store robot info in Redis
def store_robot_info(token, ip, robot_type):
    robot_info = {'ip': ip, 'robot_type': robot_type}
    redis_client.set(token, pickle.dumps(robot_info))

# get robot info from Redis
def get_robot_info(token):
    robot_data = redis_client.get(token)
    if robot_data:
        return pickle.loads(robot_data)
    return None

def get_robot_from_token(token):
    try:
        # Decode the token
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print(f'Decoded token data: {data}')  

        # Retrieve robot info from Redis
        robot_info = get_robot_info(token)
        if robot_info:
            print(f'Robot info from Redis: {robot_info}')  
            ip = robot_info['ip']
            robot_type = robot_info['robot_type']
            RobotClass = ROBOT_SUBCLASSES.get(robot_type)
            if RobotClass:
                return RobotClass(ip), None
            else:
                return None, 'Unknown robot type'
        else:
            return None, 'Robot data not found in Redis'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'

# extract token and get robot instance
def get_robot_from_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, jsonify({'message': 'Missing token'}), 401

    token = auth_header.split()[1]
    robot, error = get_robot_from_token(token)
    if error:
        return None, jsonify({'message': error}), 401

    # Ensure the robot is logged in
    try:
        robot.login()
    except Exception as e:
        return None, jsonify({'message': f'Error during robot login: {e}'}), 500

    return robot, None, None    

### Endpoints

# Route to select robot type and generate token
@app.route('/select_robot_type', methods=['POST'])
def select_robot_type():
    data = request.json
    ip = data.get('ip')  # Get IP from the request payload
    robot_type = data.get('robot_type')

    if not ip:
        return jsonify({'message': 'IP address is required'}), 400

    if robot_type not in ROBOT_SUBCLASSES:
        return jsonify({'message': 'Invalid robot type'}), 400

    token = generate_token(ip, robot_type)
    store_robot_info(token, ip, robot_type)
    return jsonify({'token': token})

# Route to set IP and initialize robot based on token
@app.route('/set_ip', methods=['POST'])
def set_ip():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code

    # Invalidate the old token by deleting the robot data from Redis
    auth_header = request.headers.get('Authorization')
    token = auth_header.split()[1]
    redis_client.delete(token)

    # Generate a new token with the new IP
    data = request.json
    new_ip = data.get('ip')
    if not new_ip:
        return jsonify({'message': 'New IP address is required'}), 400

    new_token = generate_token(new_ip, robot.__class__.__name__)
    robot.set_ip(new_ip)
    store_robot_info(new_token, new_ip, robot.__class__.__name__)

    # Ensure the robot is logged in with the new IP
    try:
        robot.login()
    except Exception as e:
        print(f'Error during robot login: {e}')
        return jsonify({'message': 'Error during robot login'}), 500

    return jsonify({'message': f'{robot.__class__.__name__} initialized and logged in successfully with new IP {robot.ip}', 'token': new_token})

# Route to power on the robot based on token
@app.route('/power_on', methods=['POST'])
def power_on():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    try:
        robot.power_on()
    except Exception as e:
        print(f'Error during robot power on: {e}')
        return jsonify({'message': 'Error during robot power on'}), 500

    return jsonify({'message': f'{robot.__class__.__name__} powered on successfully with IP {robot.ip}'})

# Route to enable the robot based on token
@app.route('/enable_robot', methods=['POST'])
def enable_robot():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    try:
        robot.enable_robot()
    except Exception as e:
        print(f'Error during robot enable: {e}')
        return jsonify({'message': 'Error during robot enable'}), 500

    return jsonify({'message': f'{robot.__class__.__name__} enabled successfully with IP {robot.ip}'})


# Route to enable the robot based on token
@app.route('/disable_robot', methods=['POST'])
def disable_robot():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    try:
        robot.disable_robot()
    except Exception as e:
        print(f'Error during robot disable: {e}')
        return jsonify({'message': 'Error during robot disable'}), 500

    return jsonify({'message': f'{robot.__class__.__name__} disable successfully with IP {robot.ip}'})

# Route to power off the robot based on token
@app.route('/power_off', methods=['POST'])
def power_off():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    try:
        robot.power_off()
    except Exception as e:
        print(f'Error during robot power off: {e}')
        return jsonify({'message': 'Error during robot power off'}), 500

    return jsonify({'message': f'{robot.__class__.__name__} powered off successfully with IP {robot.ip}'})

if __name__ == '__main__':
    app.run(debug=True)