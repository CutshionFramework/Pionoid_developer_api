# coding=utf-8
import time
import sys
import os

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_64_path = os.path.join(current_dir, '..', '..','..','libs_64')
sys.path.append(libs_64_path)

def main():  

    joint_pos = [1,1,1,1,1,1]
    tcp_pos = [0,0,-30,0,0,0]
    home_pos = [0,0,0,0,0,0]
    
    rc = jkrc.RC("192.168.2.29")

    rc.login()
    rc.power_on()
    rc.enable_robot()
    
    rc.joint_move(joint_pos,0,True,1)
    
    # record the start time
    start_time = time.perf_counter()
    
    rc.linear_move(tcp_pos,1,True,10)

    # record the end time
    end_time = time.perf_counter()
    
    # calculate the elapsed time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.6f}s")
    
    rc.joint_move(home_pos,0,True,1)
    print("Test End")
    
if __name__ == '__main__':
    import jkrc
    main()