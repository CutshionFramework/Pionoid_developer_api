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
from integrations.Openai_voice_control import VoiceControl
from robot_factory import voice_robot

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

# Route to disable the robot based on token
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

# Route to save the robot's joint positions
@app.route('/save_pos', methods=['POST'])
def save_pos():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    
    try:
        joint_positions = robot.get_joint_position()
        if len(joint_positions) != 6:
            return jsonify({'message': 'Invalid joint positions'}), 400
        
        # Create a hash with the joint positions
        position_hash = {
            'x': joint_positions[0],
            'y': joint_positions[1],
            'z': joint_positions[2],
            'RX': joint_positions[3],
            'RY': joint_positions[4],
            'RZ': joint_positions[5]
        }
        
        # Incremental field for move_name using Redis counter
        move_counter = redis_client.incr('move_counter')
        move_name = f'move_{move_counter}'
        position_hash['move_name'] = move_name
        
        # Store the hash in Redis
        redis_client.hset(move_name, mapping=position_hash)
        
        # Store the move_name in a sorted set with the counter as the score
        redis_client.zadd('move_names', {move_name: move_counter})
        
    except Exception as e:
        print(f'Error during saving position: {e}')
        return jsonify({'message': 'Error during saving position'}), 500

    return jsonify(position_hash)

# Route to update the move order and joint positions
@app.route('/update_move_pos', methods=['POST'])
def update_move_pos():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code

    move_name = request.json.get('move_name')
    new_order = request.json.get('new_order')
    new_joint_positions = request.json.get('joint_positions')
    
    if not move_name or new_order is None or not new_joint_positions:
        return jsonify({'message': 'move_name, new_order, and joint_positions are required'}), 400
    
    if len(new_joint_positions) != 6:
        return jsonify({'message': 'Invalid joint positions'}), 400
    
    try:
        # Retrieve the existing hash
        position_hash = redis_client.hgetall(move_name)
        if not position_hash:
            return jsonify({'message': f'{move_name} does not exist'}), 404
        
        # Update the joint positions
        position_hash = {
            'x': new_joint_positions[0],
            'y': new_joint_positions[1],
            'z': new_joint_positions[2],
            'RX': new_joint_positions[3],
            'RY': new_joint_positions[4],
            'RZ': new_joint_positions[5],
            'move_name': move_name
        }
        
        # Store the updated hash with the same key
        redis_client.hset(move_name, mapping=position_hash)
        
        # Remove the old entry from the sorted set
        redis_client.zrem('move_names', move_name)
        
        # Update the sorted set with the new order
        redis_client.zadd('move_names', {move_name: new_order})
        
    except Exception as e:
        print(f'Error during updating move order: {e}')
        return jsonify({'message': 'Error during updating move order'}), 500

    return jsonify({'message': f'Move order and joint positions updated for {move_name}'})

# Route to run all positions based on move_name
@app.route('/run_all_positions', methods=['POST'])
def run_all_positions():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    
    try:
        # Retrieve all move_name keys from the sorted set
        move_names = redis_client.zrange('move_names', 0, -1)
        
        # Retrieve and execute each position
        for move_name in move_names:
            position_hash = redis_client.hgetall(move_name)
            joint_positions = [
                float(position_hash[b'x']),
                float(position_hash[b'y']),
                float(position_hash[b'z']),
                float(position_hash[b'RX']),
                float(position_hash[b'RY']),
                float(position_hash[b'RZ'])
            ]
            robot.joint_move(joint_positions, 0, True, 1)
        
    except Exception as e:
        print(f'Error during running positions: {e}')
        return jsonify({'message': 'Error during running positions'}), 500

    return jsonify({'message': 'All positions executed successfully'})


@app.route('/delete_move', methods=['POST'])
def delete_move():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code

    move_name = request.json.get('move_name')
    
    if not move_name:
        return jsonify({'message': 'move_name is required'}), 400
    
    try:
        # Delete the move_name from the hash
        redis_client.delete(move_name)
        
        # Remove the move_name from the sorted set
        redis_client.zrem('move_names', move_name)
        
    except Exception as e:
        print(f'Error during deleting move: {e}')
        return jsonify({'message': 'Error during deleting move'}), 500

    return jsonify({'message': f'Move {move_name} deleted successfully'})

@app.route('/voice_command', methods=['POST'])
def voice_command():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code

    voice_control = VoiceControl()
    command = voice_control.recognize_speech()  # Recognize speech and get the command as text
    if command:
        voice_robot.handle_robot_commands(robot, command)  # Handle the robot's response to the command
        return jsonify({'message': f'Processed command: {command}'})
    else:
        return jsonify({'message': 'No command recognized'}), 400

if __name__ == '__main__':
    app.run(debug=True)