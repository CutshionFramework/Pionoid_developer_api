import time
import sys
import os

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_64_path = os.path.join(current_dir, '..','..','..','libs_64')
sys.path.append(libs_64_path)

def main():
    PI = 3.1415926
    home_pos = [0,0,0,0,0,0]
    joint_pos = [PI/2,PI/3,0,PI/4,0,0]
    
    rc = jkrc.RC("192.168.2.29")
    rc.login()
    rc.power_on()
    rc.enable_robot()
    
    start_time = time.perf_counter()
    
    rc.joint_move(joint_pos,0,True,1)
    
    end_time = time.perf_counter()
    
    execution_time = (end_time - start_time)
    print(f"Execution time: {execution_time:.6f}s")
    
    rc.joint_move(home_pos,0,True,1)
    print("Test End")

if __name__ == '__main__':
    import jkrc
    main()
    