import sys
import os
import time
import logging

# Add the directory containing core_robot to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core_robot import core_robot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_64_path = os.path.join(current_dir, '..', '..', '..', 'libs_64')
sys.path.append(libs_64_path)

IO_CABINET =0 #controller panel IO
IO_TOOL = 1 #Tool IO
IO_EXTEND = 2 #extension IO

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
    
    def logout(self):
        return self.robot.logout()
    
    def power_on(self):
        return self.robot.power_on()

    def power_off(self):
        return self.robot.power_off()
        
    def enable_robot(self):
        return self.robot.enable_robot()
    
    def disable_robot(self):
        return self.robot.disable_robot()
    
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
    
    def get_robot_status(self):
        return self.robot.get_robot_status()
 
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
    
    def set_analog_output(self, io_type, index, value):
        return self.robot.set_analog_output(io_type, index, value)
    
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
      
    def get_all_IO(self):
        all_IO = {
            "CABINET": {
                "dout": [],  # cabinet digital output
                "din": [],   # cabinet digital input
                "aout": [],  # cabinet analog output
                "ain": []    # cabinet analog input
            },
            "TOOL": {
                "tio_dout": [],  # tool digital output
                "tio_din": [],   # tool digital input
                "tio_ain": []    # tool analog input
            },
            "EXTEND": {
                "extio": [],  # external extension IO
                "out": [],
                "in": [], 
            }
        }

        ret = self.get_robot_status()
        
        all_IO["CABINET"]["dout"].append(ret[1][10])
        all_IO["CABINET"]["din"].append(ret[1][11])
        all_IO["CABINET"]["aout"].append(ret[1][12])
        all_IO["CABINET"]["ain"].append(ret[1][13])
        all_IO["TOOL"]["tio_dout"].append(ret[1][14])
        all_IO["TOOL"]["tio_din"].append(ret[1][15])
        all_IO["TOOL"]["tio_ain"].append(ret[1][16])
        all_IO["EXTEND"]["extio"].append(ret[1][17])
        
        return all_IO
    
    def apply_io_settings(self, all_IO):
        # Check if 'CABINET' has 'dout' and 'aout' keys and if they contain data
        print("apply_io_settings")
        if 'dout' in all_IO['CABINET'] and all_IO['CABINET']['dout']:
            for index, value in enumerate(all_IO['CABINET']['dout'][0]):
                # print(index, value)
                self.set_digital_output(IO_CABINET, index, value)

        if 'aout' in all_IO['CABINET'] and all_IO['CABINET']['aout']:
            for index, value in enumerate(all_IO['CABINET']['aout'][0]):
                self.set_analog_output(IO_CABINET, index, value)

        # Check if 'TOOL' has 'tio_dout' and 'tio_ain' keys and if they contain data
        if 'tio_dout' in all_IO['TOOL'] and all_IO['TOOL']['tio_dout']:
            for index, value in enumerate(all_IO['TOOL']['tio_dout'][0]):
                self.set_digital_output(IO_TOOL, index, value)

        if 'tio_ain' in all_IO['TOOL'] and all_IO['TOOL']['tio_ain']:
            for index, value in enumerate(all_IO['TOOL']['tio_ain'][0]):
                self.set_analog_output(IO_TOOL, index, value)

        # Check if 'EXTEND' has 'out' and 'aout' keys and if they contain data
        if 'out' in all_IO['EXTEND'] and all_IO['EXTEND']['out']:
            for index, value in enumerate(all_IO['EXTEND']['out']):
                self.set_digital_output(IO_EXTEND, index, value)

        if 'aout' in all_IO['EXTEND'] and all_IO['EXTEND']['aout']:
            for index, value in enumerate(all_IO['EXTEND']['aout']):
                self.set_analog_output(IO_EXTEND, index, value)


                  
# Example usage
if __name__ == "__main__":
    robot = JakaRobot("192.168.0.127")
    
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
    

    # Get robot status for all IO(filtered)
    ret = robot.get_robot_status()
    if ret[0] != 0:
        print("Something happened, the error code is:", ret[0])
    result = robot.get_all_IO()

    # filter out empty or zero values
    def filter_non_empty(io_dict):
        filtered_dict = {}
        for key, val in io_dict.items():
            if isinstance(val, list) and val:
                # Check if the list contains non-zero values
                non_zero_values = [item for item in val if any(item)]
                if non_zero_values:
                    filtered_dict[key] = non_zero_values
        return filtered_dict

    # Filter the result to only include non-empty values
    filtered_result = {
        category: filter_non_empty(io_dict)
        for category, io_dict in result.items()
    }

    print("get_all_IO:", filtered_result)
  
    # Get robot status for all IO(unfiltered)
    ret = robot.get_robot_status()
    if ret[0] == 0:
        # print("The robot state is:", ret[1])
        print("dout : ", ret[1][10])
        print("din : ", ret[1][11])
        print("aout : ", ret[1][12])
        print("ain : ", ret[1][13])
        print("tio_dout : ", ret[1][14])
        print("tio_din : ", ret[1][15])
        print("tio_ain : ", ret[1][16])
        print("extio : ", ret[1][17])
    else:
        print("Something happened, the error code is:", ret[0])
    
    result = robot.get_all_IO()
    print("@@@get_all_IO@@@ : ", result)
    

    
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
    
       
    # Joint move
    robot.joint_move(joint_pos=[1, 0, 0, 0, 0, 0], move_mode=1, is_block=False, speed=0.05)
    print("Wait")
    time.sleep(1)
    
    
    # Get joint position
    ret = robot.get_joint_position()
    if ret[0] == 0:
        print("The joint position is:", ret[1])
    else:
        print("Something happened, the error code is:", ret[0])
        
    # Linear move
    tcp_pos = [0, 0, 0, 0, 0, 0]
    ret = robot.linear_move(tcp_pos, move_mode=1, is_block=True, speed=10)
    print(ret[0])
    time.sleep(1)

    robot.apply_io_settings(result)
    
    robot.disable_robot()
    robot.power_off()
    
    # Logout
    robot.logout()
    