import rtde_control
import rtde_receive
import dashboard_client
import rtde_io
# from robot.core_robot import core_robot

class URRobot():
    def __init__(self, ip):
        # super().__init__()  # Initialize the parent class
        self.robot_control = rtde_control.RTDEControlInterface(ip)
        self.robot_receive = rtde_receive.RTDEReceiveInterface(ip)
        self.robot_dashboard_client = dashboard_client.DashboardClient(ip)
        self.robot_rtde_io = rtde_io.RTDEIOInterface(ip)
        self.speed = 1.0  # Default speed

    # dashboard_client
    def connect(self):
        self.robot_dashboard_client.connect()

    def is_connected(self):
        return self.robot_dashboard_client.isConnected()

    def power_on(self):
        self.robot_dashboard_client.powerOn()

    def power_off(self):
        self.robot_dashboard_client.powerOff()


    # rtde_control
    def disconnect(self):
        self.robot_control.disconnect()

    def reconnect(self):
        self.robot_control.reconnect()

    def isConnected(self):
        self.robot_control.isConnected()

    def moveJ(self, path, speed=1.0, acceleration=1.0, asynchronous=False):
        self.robot_control.moveJ(path, speed, acceleration, asynchronous)

    def moveJ_IK(self, pose, speed=1.05, acceleration=1.4, asynchronous=False):
        self.robot_control.moveJ_IK(pose, speed, acceleration, asynchronous)
    
    def moveL(self, pose, speed=0.25, acceleration=1.2, asynchronous=False):
        self.robot_control.moveL(pose, speed, acceleration, asynchronous)

    def moveL_FK(self, joint_positions, speed=0.25, acceleration=1.2, asynchronous=False):
        self.robot_control.moveL_FK(joint_positions, speed, acceleration, asynchronous)
    
    def move_path(self, path, asynchronous=False):
        self.robot_control.movePath(path, asynchronous)


    # rtde_receive
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

    def get_actual_tcp_pose(self):
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

    def get_robot_status(self):
        return self.robot_receive.getRobotStatus()

    def get_actual_digital_output_bits(self):
        return self.robot_receive.getActualDigitalOutputBits()

    def get_digital_out_state(self, output_id):
        return self.robot_receive.getDigitalOutState(output_id)

    def get_standard_analog_input_0(self):
        return self.robot_receive.getStandardAnalogInput0()

    def get_standard_analog_input_1(self):
        return self.robot_receive.getStandardAnalogInput1()

    def get_standard_analog_output_0(self):
        return self.robot_receive.getStandardAnalogOutput0()

    def get_standard_analog_output_1(self):
        return self.robot_receive.getStandardAnalogOutput1()

    def is_protective_stopped(self):
        return self.robot_receive.isProtectiveStopped()

    def is_emergency_stopped(self):
        return self.robot_receive.isEmergencyStopped()

    def get_payload(self):
        return self.robot_receive.getPayload()
    

    # rtde_io
    def set_standard_digital_out(self, output_id, signal_level):
        return self.robot_control.setStandardDigitalOut(output_id, signal_level)

    def set_configurable_digital_out(self, output_id, signal_level):
        return self.robot_control.setConfigurableDigitalOut(output_id, signal_level)

    def set_tool_digital_out(self, output_id, signal_level):
        return self.robot_control.setToolDigitalOut(output_id, signal_level)

    def set_speed_slider(self, speed):
        return self.robot_control.setSpeedSlider(speed)

    def set_analog_output_voltage(self, output_id, voltage_ratio):
        return self.robot_control.setAnalogOutputVoltage(output_id, voltage_ratio)

    def set_analog_output_current(self, output_id, current_ratio):
        return self.robot_control.setAnalogOutputCurrent(output_id, current_ratio)

    def set_input_int_register(self, input_id, value):
        return self.robot_control.setInputIntRegister(input_id, value)

    def set_input_double_register(self, input_id, value):
        return self.robot_control.setInputDoubleRegister(input_id, value)


# Example usage
if __name__ == "__main__":
    robot = URRobot("192.168.177.128")

    # connect dashboard (= jakaZu app)
    robot.connect()

    # Move to a specific joint position
    joint_positions_1 = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
    joint_positions_2 = [0.5, -1.0, 0.0, -1.0, 0.0, 0.0]
    robot.moveJ(joint_positions_1)
    robot.moveJ(joint_positions_2)
    
    # Print the current robot state
    print("Current timestamp:", robot.get_timestamp())
    print("Actual joint positions:", robot.get_actual_joint_positions())
    print("Actual TCP pose:", robot.get_actual_tcp_pose())
    print("Robot mode:", robot.get_robot_mode())
    print("Robot status:", robot.get_robot_status())

    # Powers off the robot arm.
    # robot.power_off()
