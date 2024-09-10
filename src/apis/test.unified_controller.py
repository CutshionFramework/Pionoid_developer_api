import requests
import json

# Base URL of the Flask server
BASE_URL = 'http://127.0.0.1:5000'

def log_response(response):
    """Utility function to log response status and content."""
    print('Response Status Code:', response.status_code)
    print('Response Content:', response.content)
    try:
        print('Response JSON:', response.json())
    except requests.exceptions.JSONDecodeError:
        print('Failed to decode JSON response')

# Test data
ip = '192.168.88.128'
robot_type = 'URRobot'

# 1. Select Robot Type and Generate Token
response = requests.post(f'{BASE_URL}/select_robot_type', json={'ip': ip, 'robot_type': robot_type})
print('Select Robot Type Response:', response.json())

# Extract the token from the response
token = response.json().get('token')
headers = {'Authorization': f'Bearer {token}'}

# 2. Set IP and Initialize Robot Based on Token
new_ip = '192.168.88.128'
response = requests.post(f'{BASE_URL}/set_ip', headers=headers, json={'ip': new_ip})
log_response(response)  

# 3. Power On the Robot
response = requests.post(f'{BASE_URL}/power_on', headers=headers)
log_response(response)  

# 4. Enable the Robot
response = requests.post(f'{BASE_URL}/enable_robot', headers=headers)
log_response(response) 

# 5. Disable the Robot
#response = requests.post(f'{BASE_URL}/disable_robot', headers=headers)
#log_response(response) 

# 6. Power Off the Robot
#response = requests.post(f'{BASE_URL}/power_off', headers=headers)
#log_response(response)  

# 7. Save a Position
joint_positions = [1, 0, 0, 0, 0, 0]
response = requests.post(f'{BASE_URL}/save_pos', headers=headers, json={'joint_positions': joint_positions})
log_response(response)  

# Extract the move_name from the response
move_name = response.json().get('move_name')

# 8. Update the Position Order
new_joint_positions = [0, 1, 0, 0, 0, 0]
new_order = 3  # Example new order
response = requests.post(f'{BASE_URL}/update_move_pos', headers=headers, json={
    'move_name': move_name,
    'new_order': new_order,
    'joint_positions': new_joint_positions
})
log_response(response)  

# 9. Run All Positions
response = requests.post(f'{BASE_URL}/run_all_positions', headers=headers)
log_response(response)  

# 10. Delete the Move
response = requests.post(f'{BASE_URL}/delete_move', headers=headers, json={'move_name': move_name})
log_response(response)  
