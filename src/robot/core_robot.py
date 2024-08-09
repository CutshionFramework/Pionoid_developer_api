# -*- coding: utf-8 -*-
import sys
import os
import time
import importlib.util

# Construct the absolute path to the libs_64 directory
libs_64_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'libs_64'))
sys.path.append(libs_64_path)

# Import the jkrc.pyd library
jkrc_path = os.path.join(libs_64_path, 'jkrc.pyd')
spec = importlib.util.spec_from_file_location("jkrc", jkrc_path)
jkrc = importlib.util.module_from_spec(spec)
sys.modules["jkrc"] = jkrc
spec.loader.exec_module(jkrc)


class JakaRobot:
    def __init__(self, ip):
        self.robot = jkrc.RC(ip)
        self.speed = 1.0 # Default speed

    def login(self):
        return self.robot.login()
    
    def logout(self):
        return self.robot.logout()
    
    def power_on(self):
        return self.robot.power_on()
    
    def enable_robot(self):
        return self.robot.enable_robot()
    
    def joint_move(self, joint_pos, move_mode, is_block, speed):
        return self.robot.joint_move(joint_pos=joint_pos, move_mode=move_mode, is_block=is_block, speed=speed)
    
    def motion_abort(self):
        return self.robot.motion_abort()
    
    def set_payload(self, mass, centroid):
        return self.robot.set_payload(mass=mass, centroid=centroid)
    
    def get_payload(self):
        return self.robot.get_payload()
    
    def get_robot_state(self):
        return self.robot.get_robot_state()
      
    def get_tcp_position(self):
        return self.robot.get_tcp_position()
    
    def get_tool_data(self, tool_id):
        return self.robot.get_tool_data(tool_id)
    
    def set_tool_data(self, tool_id, data, name):
        return self.robot.set_tool_data(tool_id, data, name)
    
    def get_tool_id(self):
        return self.robot.get_tool_id()
    
    def set_tool_id(self, tool_id):
        return self.robot.set_tool_id(tool_id)
    
    def get_digital_output(self, io_type, index):
        return self.robot.get_digital_output(io_type, index)
    
    def set_digital_output(self, io_type, index, value):
        return self.robot.set_digital_output(io_type, index, value)
    
    def get_joint_position(self):
        return self.robot.get_joint_position()
    
    def linear_move(self, tcp_pos, move_mode, is_block, speed):
        return self.robot.linear_move(tcp_pos, move_mode, is_block, speed)

    def control_speed(self, detected):
        if detected:
            self.speed = 0.1  
        else:
            if self.speed < 1:
                self.speed += 0.5  
        print(f"Speed adjusted to: {self.speed}")  
                  
# Example usage
if __name__ == "__main__":
    robot = JakaRobot("192.168.0.219")
    
    # Login
    robot.login()
    
    # Power on and enable robot
    robot.power_on()
    robot.enable_robot()
    
    # Set payload
    robot.set_payload(mass=1, centroid=[0.01, 0.02, 0.03])
    ret = robot.get_payload()
    if ret[0] == 0:
        print("The payload is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    # Get robot state
    ret = robot.get_robot_state()
    if ret[0] == 0:
        print("The robot state is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    # Get TCP position
    ret = robot.get_tcp_position()
    if ret[0] == 0:
        print("The TCP position is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    # Get and set tool data
    ret = robot.get_tool_data(1)
    if ret[0] == 0:
        print("The tool data is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    robot.set_tool_data(1, [0, 0, 1, 0, 0, 0], 'testlx')
    time.sleep(0.5)
    ret = robot.get_tool_data(1)
    if ret[0] == 0:
        print("The tool data is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    # Get and set tool ID
    ret = robot.get_tool_id()
    print("Tool ID:", ret)
    robot.set_tool_id(1)
    time.sleep(0.5)
    ret = robot.get_tool_id()
    print("Tool ID:", ret)
    
    # Get and set digital output
    ret = robot.get_digital_output(0, 2)
    if ret[0] == 0:
        print("The DO2 is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    robot.set_digital_output(0, 2, 1)
    time.sleep(0.1)
    ret = robot.get_digital_output(0, 2)
    if ret[0] == 0:
        print("The DO2 is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    # Get joint position
    ret = robot.get_joint_position()
    if ret[0] == 0:
        print("The joint position is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
    
    # Joint move
    robot.joint_move(joint_pos=[1, 0, 0, 0, 0, 0], move_mode=1, is_block=False, speed=0.05)
    print("Wait")
    time.sleep(2)
    
    # Linear move
    tcp_pos = [0, 0, -30, 0, 0, 0]
    ret = robot.linear_move(tcp_pos, move_mode=1, is_block=True, speed=10)
    print(ret[0])
    time.sleep(3)
    
    # Motion abort
    robot.motion_abort()
    
    # Logout
    robot.logout()