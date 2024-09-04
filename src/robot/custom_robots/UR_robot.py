import sys
import os
import time
import rtde_control
import rtde_receive
import dashboard_client
import rtde_io
# Add the directory containing core_robot to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core_robot import core_robot

class URRobot(core_robot):
    def __init__(self, ip):
        super().__init__()  # Initialize the parent class
        self.robot_control = rtde_control.RTDEControlInterface(ip)
        self.robot_receive = rtde_receive.RTDEReceiveInterface(ip)
        self.robot_dashboard_client = dashboard_client.DashboardClient(ip)
        self.robot_rtde_io = rtde_io.RTDEIOInterface(ip)

    # dashboard_client
    def login(self):
        self.robot_dashboard_client.connect()

    def is_connected(self):
        return self.robot_dashboard_client.isConnected()

    def power_on(self):
        self.robot_dashboard_client.powerOn()

    def power_off(self):
        self.robot_dashboard_client.powerOff()
    
    def enable_robot(self):
        self.robot_dashboard_client.brakeRelease()


    # rtde_control
    def logout(self):
        self.robot_control.disconnect()

    def reconnect(self):
        self.robot_control.reconnect()

    def isConnected(self):
        self.robot_control.isConnected()

    def joint_move(self, joint_pos, move_mode, is_block, speed):
        self.robot_control.moveJ(joint_pos, speed)

    def moveJ_IK(self, pose, speed=1.05, acceleration=1.4, asynchronous=False):
        self.robot_control.moveJ_IK(pose, speed, acceleration, asynchronous)
    
    def linear_move(self, tcp_pos, move_mode, is_block, speed):
        self.robot_control.moveL(tcp_pos, speed)

    def moveL_FK(self, joint_positions, speed=0.25, acceleration=1.2, asynchronous=False):
        self.robot_control.moveL_FK(joint_positions, speed, acceleration, asynchronous)
    
    def move_path(self, path, asynchronous=False):
        self.robot_control.movePath(path, asynchronous)


    # robot_receive
    def get_timestamp(self):
        return self.robot_receive.getTimestamp()

    def get_target_joint_positions(self):
        return self.robot_receive.getTargetQ()

    def get_target_joint_velocities(self):
        return self.robot_receive.getTargetQd()

    def get_target_joint_accelerations(self):
        return self.robot_receive.getTargetQdd()

    def get_target_joint_currents(self):
        return self.robot_receive.getTargetCurrent()

    def get_target_joint_moments(self):
        return self.robot_receive.getTargetMoment()

    def get_actual_joint_positions(self):
        return self.robot_receive.getActualQ()

    def get_actual_joint_velocities(self):
        return self.robot_receive.getActualQd()

    def get_actual_joint_currents(self):
        return self.robot_receive.getActualCurrent()

    def get_joint_control_outputs(self):
        return self.robot_receive.getJointControlOutput()

    def get_tcp_position(self):
        return self.robot_receive.getActualTCPPose()

    def get_actual_tcp_speed(self):
        return self.robot_receive.getActualTCPSpeed()

    def get_actual_tcp_force(self):
        return self.robot_receive.getActualTCPForce()

    def get_target_tcp_pose(self):
        return self.robot_receive.getTargetTCPPose()

    def get_target_tcp_speed(self):
        return self.robot_receive.getTargetTCPSpeed()
    
    def get_robot_mode(self):
        return self.robot_receive.getRobotMode()

    def get_robot_state(self):
        return self.robot_receive.getRobotStatus()
    
    def get_actual_digital_input_bits(self):
        return self.robot_receive.getActualDigitalInputBits()

    def get_actual_digital_output_bits(self):
        return self.robot_receive.getActualDigitalOutputBits()

    def get_digital_out_state(self, output_id):
        return self.robot_receive.getDigitalOutState(output_id)
    
    def get_digital_in_state(self, input_id):
        return self.robot_receive.getDigitalInState(input_id)

    def get_standard_analog_input_0(self):
        return self.robot_receive.getStandardAnalogInput0()

    def get_standard_analog_input_1(self):
        return self.robot_receive.getStandardAnalogInput1()

    def get_standard_analog_output_0(self):
        return self.robot_receive.getStandardAnalogOutput0()

    def get_standard_analog_output_1(self):
        return self.robot_receive.getStandardAnalogOutput1()
    
    def get_tool_digital_output(self,output_id):
        return self.robot_receive.getToolDigitalOut(output_id)

    def is_protective_stopped(self):
        return self.robot_receive.isProtectiveStopped()

    def is_emergency_stopped(self):
        return self.robot_receive.isEmergencyStopped()

    def get_payload(self):
        return self.robot_receive.getPayload()
    
    def get_actual_tool_accelerometer(self):
        return self.robot_receive.getActualToolAccelerometer()

    # rtde_io
    def set_standard_digital_out(self, output_id, signal_level):
        return self.robot_rtde_io.setStandardDigitalOut(output_id, signal_level)

    def set_configurable_digital_out(self, output_id, signal_level):
        return self.robot_rtde_io.setConfigurableDigitalOut(output_id, signal_level)

    def set_tool_digital_out(self, output_id, signal_level):
        return self.robot_rtde_io.setToolDigitalOut(output_id, signal_level)

    def set_speed_slider(self, speed):
        return self.robot_rtde_io.setSpeedSlider(speed)

    def set_analog_output_voltage(self, output_id, voltage_ratio):
        return self.robot_rtde_io.setAnalogOutputVoltage(output_id, voltage_ratio)

    def set_analog_output_current(self, output_id, current_ratio):
        return self.robot_rtde_io.setAnalogOutputCurrent(output_id, current_ratio)

    def set_input_int_register(self, input_id, value):
        return self.robot_rtde_io.setInputIntRegister(input_id, value)

    def set_input_double_register(self, input_id, value):
        return self.robot_rtde_io.setInputDoubleRegister(input_id, value)
    
    def get_active_digital_output(self):
        # Set delay to ensure the result is reflected
        time.sleep(0.1)
        decimal_output_bits = self.robot_receive.getActualDigitalOutputBits()
        
        # Process the bits
        result, enable_DO = self.decimal_to_binary_and_categorize(decimal_output_bits)
        
        # Print the categorized bits
        print("[Enabled DO]")
        for category, bits in enable_DO.items():
            print(f"{category}: {bits}")
        
        return decimal_output_bits

    def set_digital_output(self, io_type, index, value):
        if io_type == 0:
            return self.set_standard_digital_out(index, value)
        elif io_type == 1:
            return self.set_tool_digital_out(index, value)
        elif io_type == 2:
            return self.set_configurable_digital_out(index, value)
        else:
            raise ValueError("Invalid io_type")
        

    # Helper - Convert decimal result to binary and categorize each DO
    def decimal_to_binary_and_categorize(self, n):
        # Convert decimal to binary
        binary = bin(n)[2:]  # Remove the '0b' prefix from the binary representation
        
        # Pad the binary number to ensure it has at least 18 bits
        binary = binary.zfill(18)

        # Reverse the binary string to access from the least significant bit
        reversed_binary = binary[::-1]

        # Categorize based on specified bit ranges
        categories = {
            "CABINET-STANDARD": reversed_binary[:8][::-1],       # 0-7 bits standard
            "EXTEND-CONFIG": reversed_binary[8:16][::-1], # 8-15 bits configurable
            "TOOL": reversed_binary[16:18][::-1]         # 16-17 bits tool
        }

        # Initialize the enable DO dictionary to store bit positions with value '1'
        enable_DO = {
            "CABINET-STANDARD": [],
            "EXTEND-CONFIG": [],
            "TOOL": []
        }
        
        # Populate the enable DO dictionary with bit positions that are '1'
        for category, bits in categories.items():
            for i, bit in enumerate(bits[::-1]):  # Iterate from the least significant bit
                if bit == '1':
                    enable_DO[category].append(i)

        return categories, enable_DO

# Example usage
if __name__ == "__main__":
    robot = URRobot("192.168.88.128")

    # connect dashboard (= jakaZu app)
    robot.login()

    # Move to a specific joint position
    joint_positions_1 = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
    joint_positions_2 = [0.5, -1.0, 0.0, -1.0, 0.0, 0.0]
    robot.joint_move(joint_positions_1, 0, True, 1)
    robot.joint_move(joint_positions_2, 0, True, 1)
    
    # Print the current robot receive
    
    print("Current timestamp:", robot.get_timestamp())
    print("Actual joint positions:", robot.get_actual_joint_positions())
    print("Actual TCP pose:", robot.get_tcp_position())
    print("Robot mode:", robot.get_robot_mode())
    print("Robot status:", robot.get_robot_state())
    print("Get standard analog output1", robot.get_standard_analog_output_1())
    print("Get standard analog input1", robot.get_standard_analog_input_1())
    print("Get actual tool accelerometer", robot.get_actual_tool_accelerometer())
    print("Get payload", robot.get_payload())
    
    # Print the current robot io 
    
    print("Set standard DO", robot.set_standard_digital_out(2, False))
    print("Set configurable DO", robot.set_configurable_digital_out(2, False))
    print("Set tool DO", robot.set_tool_digital_out(1, False)) 
    robot.set_digital_output(1, 0, 0)
    print("bit:", robot.get_active_digital_output(), flush=True)

            
    # Powers off the robot arm.
    # robot.power_off()