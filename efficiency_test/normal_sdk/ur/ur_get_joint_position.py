import time

def main():
    robot_control = rtde_control.RTDEControlInterface("192.168.19.128")
    robot_receive = rtde_receive.RTDEReceiveInterface("192.168.19.128")
    
    PI=3.1415926
    joint_pos = [-(PI/2),-(PI/3),0,-(PI/4),0,0]
    home_pos = [-1.6006999999999998, -1.7271, -2.2029999999999994, -0.8079999999999998, 1.5951, -0.030999999999999694]
    
    # record the start time
    start_time = time.perf_counter()
    
    robot_control.moveJ(joint_pos,1)
    robot_receive.getActualQ()
    
    # record the end time
    end_time = time.perf_counter()
    
    # calculate the elapsed time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.6f}s")
    
    robot_control.moveJ(home_pos,1)
    print("Test END")
    
if __name__ == '__main__':
    import rtde_control
    import rtde_receive
    main()