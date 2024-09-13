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
# CORS(app)  # Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])


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
@app.route('/set_ip', methods=['POST'])
def set_ip():
    data = request.json
    new_ip = data.get('ip')
    robot_type = data.get('robot_type')

    if not new_ip:
        return jsonify({'message': 'IP address is required'}), 400

    if not robot_type:
        return jsonify({'message': 'Robot type is required'}), 400

    if robot_type not in ROBOT_SUBCLASSES:
        return jsonify({'message': 'Invalid robot type'}), 400

    new_token = generate_token(new_ip, robot_type)
    store_robot_info(new_token, new_ip, robot_type)

    RobotClass = ROBOT_SUBCLASSES.get(robot_type)
    if not RobotClass:
        return jsonify({'message': 'Unknown robot type'}), 400

    robot = RobotClass(new_ip)
    robot.set_ip(new_ip)

    try:
        robot.login()
    except Exception as e:
        print(f'Error during robot login: {e}')
        return jsonify({'message': 'Error during robot login'}), 500

    return jsonify({'message': f'{robot.__class__.__name__} initialized and logged in successfully with IP {robot.ip}', 'token': new_token})

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
@app.route('/save_move', methods=['POST'])
def save_move():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    
    try:
        joint_positions_tuple = robot.get_joint_position()
        print(f"Joint positions: {joint_positions_tuple}")

        all_IO = robot.get_all_IO()
        print(f"IO data: {all_IO}")

        joint_positions = joint_positions_tuple[1]

        if len(joint_positions) != 6:
            return jsonify({'message': 'Invalid joint positions'}), 400
        
        # Create a hash with the joint positions
        position_hash = {
            'x': joint_positions[0],
            'y': joint_positions[1],
            'z': joint_positions[2],
            'RX': joint_positions[3],
            'RY': joint_positions[4],
            'RZ': joint_positions[5],
            'IO': all_IO
        }

        # Convert position_hash keys and values to str
        position_hash_str = {str(k): str(v) for k, v in position_hash.items()}

        # Incremental field for move_name using Redis counter
        move_counter = redis_client.incr('move_counter')
        move_name = f'move_{move_counter}'
        position_hash_str['move_name'] = move_name
        
        # Store the hash in Redis
        redis_client.hset(move_name, mapping=position_hash_str)
        
        # Re-adjust the scores for consistent ordering
        _reorder_scores()

        # Add the new move_name to the sorted set with the highest score (last position)
        max_score = redis_client.zcard('move_names') + 1  # max score is the next available number
        redis_client.zadd('move_names', {move_name: max_score})
        
    except Exception as e:
        print(f'Error during saving position: {e}')
        return jsonify({'message': 'Error during saving position'}), 500

    return jsonify(position_hash)

@app.route('/update_move', methods=['PUT'])
def update_move():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code

    # Retrieve the data from the request
    original_name = request.json.get('originalName')
    updated_item = request.json.get('updatedItem', {})

    new_joint_positions = [
        float(updated_item.get('x', 0)),
        float(updated_item.get('y', 0)),
        float(updated_item.get('z', 0)),
        float(updated_item.get('rx', 0)),
        float(updated_item.get('ry', 0)),
        float(updated_item.get('rz', 0))
    ]
    new_IO = robot.get_all_IO()
    
    if not original_name or len(new_joint_positions) != 6:
        return jsonify({'message': 'originalName and valid joint positions are required'}), 400
    
    try:
        # Retrieve the existing hash
        position_hash = redis_client.hgetall(original_name)
        if not position_hash:
            return jsonify({'message': f'{original_name} does not exist'}), 404
        
        # Retrieve the current score for the original_name
        current_score = redis_client.zscore('move_names', original_name)
        if current_score is None:
            return jsonify({'message': 'Failed to retrieve the current score'}), 500
        
        # Update the joint positions and IO
        new_name = updated_item.get('move_name', original_name)
        position_hash_str = {
            'x': str(new_joint_positions[0]),
            'y': str(new_joint_positions[1]),
            'z': str(new_joint_positions[2]),
            'RX': str(new_joint_positions[3]),
            'RY': str(new_joint_positions[4]),
            'RZ': str(new_joint_positions[5]),
            'IO': str(new_IO)
        }
        
        # Remove the old entry from the sorted set
        redis_client.zrem('move_names', original_name)
        
        # Store the updated hash with the new key
        redis_client.hset(new_name, mapping=position_hash_str)
        
        # Add the updated name to the sorted set with the original score
        redis_client.zadd('move_names', {new_name: current_score})
        
        # If the new name is different, remove the old entry
        if new_name != original_name:
            redis_client.delete(original_name)
        
    except Exception as e:
        print(f'Error during updating move order: {e}')
        return jsonify({'message': 'Error during updating move order'}), 500

    return jsonify({'message': f'Move order and joint positions updated for {original_name}'})

@app.route('/copy_move', methods=['POST'])
def copy_move():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code

    data = request.json
    original_name = data.get('originalName')

    if not original_name:
        return jsonify({'message': 'originalName is required'}), 400

    try:
        # Retrieve the existing hash
        existing_hash = redis_client.hgetall(original_name)
        if not existing_hash:
            return jsonify({'message': f'{original_name} does not exist'}), 404

        # Generate the new move_name by appending '_copy' to the original_name
        new_move_name = f'{original_name}_copy'

        # Prepare the copied item data for storage
        copied_item_data = {
            'x': existing_hash.get(b'x', b'').decode('utf-8'),
            'y': existing_hash.get(b'y', b'').decode('utf-8'),
            'z': existing_hash.get(b'z', b'').decode('utf-8'),
            'RX': existing_hash.get(b'RX', b'').decode('utf-8'),
            'RY': existing_hash.get(b'RY', b'').decode('utf-8'),
            'RZ': existing_hash.get(b'RZ', b'').decode('utf-8'),
            'IO': existing_hash.get(b'IO', b'').decode('utf-8')
        }

        # Log the copied item data to debug
        print(f'Copied item data: {copied_item_data}')

        # Store the copied item in Redis with the new_move_name
        redis_client.hset(new_move_name, mapping=copied_item_data)

        # Store the new move_name in a sorted set with the highest score
        current_max_score = redis_client.zrange('move_names', -1, -1, withscores=True)
        new_score = (current_max_score[0][1] + 1) if current_max_score else 0
        redis_client.zadd('move_names', {new_move_name: new_score})

    except Exception as e:
        print(f'Error during copying position: {e}')
        return jsonify({'message': 'Error during copying position'}), 500

    return jsonify({'message': f'Copied item saved successfully as {new_move_name}'})

@app.route('/delete_move', methods=['DELETE'])
def delete_move():
    move_name = request.json.get('move_name')
    
    if not move_name:
        return jsonify({'message': 'move_name is required'}), 400
    
    try:
        # Delete the move from the hash and sorted set
        redis_client.delete(move_name)
        redis_client.zrem('move_names', move_name)

        # Re-adjust the scores to maintain sequential order
        _reorder_scores()

    except Exception as e:
        print(f'Error during deleting move: {e}')
        return jsonify({'message': 'Error during deleting move'}), 500

    return jsonify({'message': f'Move {move_name} deleted successfully'})

@app.route('/reorder_moves', methods=['POST'])
def reorder_moves():
    data = request.json
    move_name = data.get('move_name')
    new_index = data.get('new_index')

    if not move_name or new_index is None:
        return jsonify({'message': 'move_name and new_index are required'}), 400

    try:
        adjusted_index = new_index + 1

        # Retrieve all move_names and scores
        move_names_with_scores = redis_client.zrange('move_names', 0, -1, withscores=True)

        # Remove the current move_name
        redis_client.zrem('move_names', move_name)

        # Re-adjust scores of remaining items excluding the newly added item
        new_list = []
        for i, (name, score) in enumerate(move_names_with_scores):
            decoded_name = name.decode('utf-8')
            if decoded_name != move_name:
                new_list.append((decoded_name, i + 1))  # Assign scores sequentially starting from 1

        # Insert move_name at the appropriate position in the newly rearranged list
        new_list.insert(adjusted_index - 1, (move_name, adjusted_index))  # Insert at adjusted_index

        # Update the sorted set in Redis
        redis_client.zremrangebyrank('move_names', 0, -1)
        for i, (name, _) in enumerate(new_list):
            redis_client.zadd('move_names', {name: i + 1})  # Reorder scores starting from 1 for all items

    except Exception as e:
        print(f'Error during reordering moves: {e}')
        return jsonify({'message': 'Error during reordering moves'}), 500

    return jsonify({'message': f'Move {move_name} reordered successfully to position {new_index}'})

def _reorder_scores():
    try:
        # Retrieve all moves in the sorted set
        move_names = redis_client.zrange('move_names', 0, -1)

        # Assign new sequential scores
        for index, move_name in enumerate(move_names):
            redis_client.zadd('move_names', {move_name: index + 1})

    except Exception as e:
        print(f'Error during reordering scores: {e}')

@app.route('/get_moves', methods=['GET'])
def get_moves():
    try:
        move_names = redis_client.zrange('move_names', 0, -1)
        
        movements = []
        
        for move_name in move_names:
            position_hash = redis_client.hgetall(move_name)
            joint_positions = {
                'x': float(position_hash[b'x']),
                'y': float(position_hash[b'y']),
                'z': float(position_hash[b'z']),
                'RX': float(position_hash[b'RX']),
                'RY': float(position_hash[b'RY']),
                'RZ': float(position_hash[b'RZ']),
                'move_name': move_name.decode('utf-8'),
                'IO': position_hash.get(b'IO', b'').decode('utf-8')  # Ensure IO data is in string format
            }
            movements.append(joint_positions)
        
        return jsonify(movements)

    except Exception as e:
        print(f'Error during fetching movements: {e}')
        return jsonify({'message': 'Error fetching movements'}), 500

@app.route('/run_all_moves', methods=['POST'])
def run_all_moves():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    
    # Get the 'times' parameter from the request body
    data = request.get_json()
    times = int(data.get('times', 1))  # Default to 1 if 'times' is not provided

    try:
        # Retrieve all move_name keys from the sorted set
        move_names = redis_client.zrange('move_names', 0, -1)
        
        for _ in range(times):
            # Retrieve and execute each position
            for move_name in move_names:
                move_name = move_name.decode('utf-8')
                
                position_hash = redis_client.hgetall(move_name)
                
                # Log the position hash to debug the issue
                print(f'Position Hash: {position_hash}')
                
                # Ensure all position values exist and are valid floats
                try:
                    joint_positions = [
                        float(position_hash.get(b'x', 0)),  # Default to 0 if key is missing
                        float(position_hash.get(b'y', 0)),
                        float(position_hash.get(b'z', 0)),
                        float(position_hash.get(b'RX', 0)),
                        float(position_hash.get(b'RY', 0)),
                        float(position_hash.get(b'RZ', 0))
                    ]
                except ValueError as ve:
                    print(f'Error converting joint positions to float: {ve}')
                    return jsonify({'message': 'Invalid joint position values in Redis'}), 500

                # Ensure IO data is decoded and valid
                IO = position_hash.get(b'IO', b'').decode('utf-8')  # Ensure IO data is in string format

                # Execute the robot movement
                robot.joint_move(joint_positions, 0, True, 1)  # Optional safezone

                # # Apply IO settings if IO data is present
                # if IO:
                #     robot.apply_io_settings(eval(IO))
        
    except Exception as e:
        print(f'Error during running positions: {e}')
        return jsonify({'message': 'Error during running positions'}), 500

    return jsonify({'message': 'All positions executed successfully'})

@app.route('/get_io_status', methods=['GET'])
def get_io_status():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    
    try:
        all_IO = robot.get_all_IO()
        
        return jsonify(all_IO)

    except Exception as e:
        print(f'Error during fetching movements: {e}')
        return jsonify({'message': 'Error fetching movements'}), 500
    
@app.route('/set_io_status', methods=['POST'])
def set_io_status():
    robot, error_response, status_code = get_robot_from_request()
    if error_response:
        return error_response, status_code
    
    data = request.json
    io_type_str = data.get('io_type')  # 클라이언트에서 문자열로 넘어오는 io_type
    io_type_mapping = {
        'Cabinet': 0,
        'Tool': 1,
        'Extend': 2
    }
    
    io_type = io_type_mapping.get(io_type_str)
    
    if io_type is None:  # 올바르지 않은 io_type인 경우
        return jsonify({'message': 'Invalid io_type'}), 400

    io_signal_type = data.get('io_signal_type')
    index = data.get('index')
    value = data.get('value')
    print("result@@@ : ", io_type, io_signal_type, index, value)

    try:
        if io_type == 0:  # Cabinet
            if io_signal_type.startswith('DO'):
                print("result : ", io_type, io_signal_type, index, value)
                robot.set_digital_output(io_type, index, value)
            elif io_signal_type.startswith('AO'):
                print("result : ", io_type, io_signal_type, index, value)
                robot.set_analog_output(io_type, index, value)
        elif io_type == 1:  # Tool
            if io_signal_type.startswith('DO'):
                print("result : ", io_type, io_signal_type, index, value)
                robot.set_digital_output(io_type, index, value)
        elif io_type == 2:  # Extend
            print('Not sure how to use it')
            # if io_signal_type.startswith('extio'):
            #     robot.set_digital_output(io_type, index, value)  # Assuming extio is digital
            # elif io_signal_type.startswith('out'):
            #     robot.set_digital_output(io_type, index, value)


        return jsonify({'message': 'IO status updated successfully'})

    except Exception as e:
        print(f'Error during setting IO status: {e}')
        return jsonify({'message': 'Error setting IO status'}), 500


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