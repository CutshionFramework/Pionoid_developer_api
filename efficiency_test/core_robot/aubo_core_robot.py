import sys
import os

# Add the directory containing core_robot to the system path
# Add the src/robot directory path to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
core_robot_path = os.path.abspath(os.path.join(current_dir, '..', '..','src', 'robot'))
sys.path.append(core_robot_path)


# import the core_robot module
from core_robot import core_robot 

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
Dlls_path = os.path.join(current_dir, '..', '..', 'Dlls')
sys.path.append(Dlls_path)

