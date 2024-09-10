# src/robot/core_robot.py
from abc import ABC, abstractmethod

class core_robot(ABC):
    def __init__(self):  
        self.ip = None
        self.speed = 1.0  # Default speed
    
    def set_ip(self, ip):
        """Set the IP address of the robot."""
        self.ip = ip
        # Default implementation that can be used by subclasses

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def power_on(self):
        pass

    @abstractmethod
    def power_off(self):
        pass

    @abstractmethod
    def enable_robot(self):
        pass

    @abstractmethod
    def disable_robot(self):
        pass

    @abstractmethod
    def joint_move(self, joint_pos, move_mode, is_block, speed):
        pass

    @abstractmethod
    def linear_move(self, tcp_pos, move_mode, is_block, speed):
        pass

    @abstractmethod
    def get_robot_state(self):
        pass

    @abstractmethod
    def get_tcp_position(self):
        pass

    @abstractmethod
    def get_active_digital_output(self):
        pass

    @abstractmethod
    def set_digital_output(self, io_type, index, value):
        pass

    @abstractmethod
    def get_all_IO(self):
        pass

    @abstractmethod
    def get_robot_status(self):
        pass
    
