import rtde_control
import rtde_receive
import dashboard_client
# from robot.core_robot import core_robot

class URRobot():
    def __init__(self, ip):
        # super().__init__()  # Initialize the parent class
        self.robot_control = rtde_control.RTDEControlInterface(ip)
        self.robot_receive = rtde_receive.RTDEReceiveInterface(ip)
        self.robot_dashboard_client = dashboard_client.DashboardClient(ip)
        self.speed = 1.0  # Default speed
    
    def connect(self):
        self.robot_dashboard_client.connect()

    def is_connected(self):
        return self.robot_dashboard_client.isConnected()

    def power_on(self):
        try:
            self.robot_dashboard_client.powerOn()
            print("Power on command sent.")
        except Exception as e:
            print(f"Power on failed: {e}")

    def power_off(self):
        try:
            self.robot_dashboard_client.powerOff()
            print("Power off command sent.")
        except Exception as e:
            print(f"Power off failed: {e}")
    
    def move_to_joint_position(self, joint_q):
        self.robot_control.moveJ(joint_q)

    def get_tcp_pose(self):
        return self.robot_receive.getActualTCPPose()

    def get_joint_positions(self):
        return self.robot_receive.getActualQ()

    def stop_robot(self):
        self.robot_control.stopScript()


# Example usage
if __name__ == "__main__":
    robot = URRobot("192.168.177.128")

    # connect dashboard (= jakaZu app)
    # but, if robot status is power off or idle -> not working everything
    robot.connect()
    print("connect? : ", robot.is_connected())
    
    # Powers on the robot arm.
    robot.power_on()

    # joint move
    joint_q = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
    robot.move_to_joint_position(joint_q)

    # get status
    actual_TCP_pose = robot.get_tcp_pose()
    joint_positions = robot.get_joint_positions()
    print("current tcp : ", actual_TCP_pose)
    print("current joint pos : ", joint_positions)

    # This function will terminate the script on controller.
    robot.stop_robot()

    # Powers off the robot arm.
    robot.power_off()
