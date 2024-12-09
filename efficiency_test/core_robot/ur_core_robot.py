import sys
import os
import time
import rtde_control
import rtde_receive
import dashboard_client
import rtde_io

# Add the directory containing core_robot to the system path
# Add the src/robot directory path to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
core_robot_path = os.path.abspath(os.path.join(current_dir, '..', '..','src', 'robot'))
sys.path.append(core_robot_path)

# import the core_robot module
from core_robot import core_robot

class URRobot(core_robot):
    def __init__(self, ip):
        super().__init__()  # Initialize the parent class
        self.robot_control = rtde_control.RTDEControlInterface(ip)
        self.robot_receive = rtde_receive.RTDEReceiveInterface(ip)
        self.robot_dashboard_client = dashboard_client.DashboardClient(ip)
        self.robot_rtde_io = rtde_io.RTDEIOInterface(ip)
        
    def login(self):
        self.robot_dashboard_client.connect()
        
    def power_on(self):
        if not self.is_connected():
            raise RuntimeError("Dashboard client is not connected")
        self.robot_dashboard_client.powerOn()
        
    def enable_robot(self):
        if not self.is_connected():
            raise RuntimeError("Dashboard client is not connected")
        self.robot_dashboard_client.brakeRelease()
        
    def joint_move(self, joint_pos, move_mode, is_block, speed):
        self.robot_control.moveJ(joint_pos, speed)
        
    def linear_move(self, tcp_pos, move_mode, is_block, speed):
        self.robot_control.moveL(tcp_pos, speed)
        
    def get_joint_position(self):
        return self.robot_receive.getActualQ()
    
    def get_tcp_position(self):
        return self.robot_receive.getActualTCPPose()
    
    def get_robot_status(self):
        return self.robot_receive.getRobotStatus()
    
    
    
# Example usage
if __name__ == "__main__":
    robot = URRobot("192.168.19.128")
    
    joint_pos = [-3.14,-1.,0.5, -1.,-1.5,0]
    home_pos = [-1.6006999999999998, -1.7271, -2.2029999999999994, -0.8079999999999998, 1.5951, -0.030999999999999694]
    tcp_pos = [-0.143, -0.435, 0.20, -0.001, 3.12, 0.04]
    
    # robot.joint_move(joint_pos,0,True,1)
    # record the start time
    start_time = time.perf_counter()
    
    robot.linear_move(tcp_pos,0,True,1)
    robot.get_tcp_position()
    
    # record the end time
    end_time = time.perf_counter()
    
    # calculate the elapsed time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.6f}s")
    
    robot.joint_move(home_pos,0,True,1)
    print("Test END")