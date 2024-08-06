from Basic_Operations_4_1 import *
from Force_control_4_9 import *
from Kinematics_4_7 import *
from Movements_4_2 import *
from safety_status_settings_4_4 import *
from Servo_Mode_4_8 import *
from set_get_Operation_info_4_3 import *

def main():
    # Example usage of get_joint_position
    print("Getting joint position...")
    get_joint_position.main_get_joint_position()

    # Example usage of joint_move with different values
    print("Moving joints to first position...")
    joint_pos1 = [PI/2, PI/3, 0, PI/4, 0, 0]
    joint_move.perform_joint_move(joint_pos1)

    print("Moving joints to second position...")
    joint_pos2 = [PI/4, PI/6, 0, PI/8, 0, 0]
    joint_move.perform_joint_move(joint_pos2)

    # Example usage of get_robot_status
    print("Getting robot status...")
    get_robot_status.main_get_robot_status()

    # Example usage of get_robot_state
    print("Getting robot state...")
    get_robot_state.main_get_robot_state()

    # Example usage of set_get_digital_output
    print("Setting and getting digital output...")
    set_get_digital_output.main_set_get_digital_output()

    # Example usage of get_controller_ip
    print("Getting controller IP...")
    get_controller_ip.main_get_controller_ip()

    # Example usage of enable_admittance_ctrl
    print("Enabling admittance control...")
    enable_admittance_ctrl.main_enable_admittance_ctrl()

if __name__ == "__main__":
    main()