# src/robot/core_robot.py
# example setup, future use of ABC classes for common interface & structure 

class core_robot:
    def __init__(self):
        self.id = None
        self.type = None

    def perform_task(self, task: str):
        """
        Perform a specific task. This method should be overridden in derived classes.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def get_oper_status(self) -> dict:
        """
        Get the current status of the robot. This method can be overridden if needed.
        """
        return {
            "id": self.id,
            "type": self.type,
            "status": "Unknown"
        }
    
    # Additional methods common to all robots can be added here
