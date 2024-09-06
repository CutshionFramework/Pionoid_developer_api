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
ip = '192.168.0.112'
robot_type = 'JakaRobot'

# 1. Select Robot Type and Generate Token
response = requests.post(f'{BASE_URL}/select_robot_type', json={'ip': ip, 'robot_type': robot_type})
print('Select Robot Type Response:', response.json())

# Extract the token from the response
token = response.json().get('token')

# 2. Set IP and Initialize Robot Based on Token
new_ip = '192.168.0.112'
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(f'{BASE_URL}/set_ip', headers=headers, json={'ip': new_ip})
log_response(response)  # Use the utility function

# 3. Power On the Robot
response = requests.post(f'{BASE_URL}/power_on', headers=headers)
log_response(response)  # Use the utility function

# 4. Enable the Robot
response = requests.post(f'{BASE_URL}/enable_robot', headers=headers)
log_response(response)  # Use the utility function

# 5. Disable the Robot
response = requests.post(f'{BASE_URL}/disable_robot', headers=headers)
log_response(response)  # Use the utility function

# 6. Power Off the Robot
response = requests.post(f'{BASE_URL}/power_off', headers=headers)
log_response(response)  # Use the utility function