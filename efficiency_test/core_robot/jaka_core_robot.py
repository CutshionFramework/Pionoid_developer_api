import sys
import os
import time
import logging

# Add the directory containing core_robot to the system path
# Add the src/robot directory path to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
core_robot_path = os.path.abspath(os.path.join(current_dir, '..', '..','src', 'robot'))
sys.path.append(core_robot_path)


# import the core_robot module
from core_robot import core_robot 


# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_64_path = os.path.join(current_dir, '..', '..', 'libs_64')
sys.path.append(libs_64_path)

# Import the jkrc.pyd library
try:
    import jkrc
except ImportError as e:
    logging.error(f"Failed to import jkrc: {e}")
    sys.exit(1)
    

class JakaRobot(core_robot):
    def __init__(self, ip):
        super().__init__()  # Initialize the parent class
        self.robot = jkrc.RC(ip)
        
    def login(self):
        return self.robot.login()
    
    def power_on(self):
        return self.robot.power_on()
    
    def enable_robot(self):
        return self.robot.enable_robot()
    
    def joint_move(self, joint_pos, move_mode, is_block, speed):
        return self.robot.joint_move(joint_pos=joint_pos, move_mode=move_mode, is_block=is_block, speed=speed)
    
    def linear_move(self, tcp_pos, move_mode, is_block, speed):
        return self.robot.linear_move(tcp_pos, move_mode, is_block, speed)
    
    def get_tcp_position(self):
        return self.robot.get_tcp_position()
    
    def get_robot_status(self):
        return self.robot.get_robot_status()
    
    def get_joint_position(self):
        return self.robot.get_joint_position()
    

# Example usage
if __name__ == "__main__":

    PI=3.1415926
    joint_pos1 = [PI/2,PI/3,0,PI/4,0,0]
    joint_pos2 = [1,1,1,1,1,1]
    tcp_pos = [0,0,-30,0,0,0]
    home_pos = [0,0,0,0,0,0]
    
    robot = JakaRobot("192.168.2.29")
   
    robot.login()
    robot.power_on()
    robot.enable_robot()
    
    start_time = time.perf_counter()
    
    # robot.joint_move(joint_pos1,move_mode=0, is_block=True, speed=1)
    
    # robot.linear_move(tcp_pos,1,True,10)
    # robot.joint_move(zero_pos,move_mode=0, is_block=True, speed=1)
    
    # robot.get_tcp_position()
    robot.joint_move(joint_pos2,move_mode=0, is_block=True, speed=1)
    # robot.get_robot_status()
    robot.get_joint_position()
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time   
    print(f"Execution time: {execution_time:.6f}s")
    
    robot.joint_move(home_pos,move_mode=0, is_block=True, speed=1)
    print("Test End")
    
    