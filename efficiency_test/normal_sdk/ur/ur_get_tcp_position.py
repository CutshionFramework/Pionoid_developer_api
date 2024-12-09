import time

def main():
    robot_control = rtde_control.RTDEControlInterface("192.168.19.128")
    robot_receive = rtde_receive.RTDEReceiveInterface("192.168.19.128")
    
    home_pos = [-1.6006999999999998, -1.7271, -2.2029999999999994, -0.8079999999999998, 1.5951, -0.030999999999999694]
    tcp_pos = [-0.143, -0.435, 0.20, -0.001, 3.12, 0.04]
    
    # record the start time
    start_time = time.perf_counter()
    
    robot_control.moveL(tcp_pos,1)
    robot_receive.getActualTCPPose()
    
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