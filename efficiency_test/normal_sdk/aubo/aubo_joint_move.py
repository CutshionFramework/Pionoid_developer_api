#! /usr/bin/env python
# coding=utf-8
import time

import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import Process, Queue
import os
from math import pi
import sys

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
Dll_path = os.path.join(current_dir, '..','..','..','Dlls')
sys.path.append(Dll_path)


class AuboRobot():
    __client_count = 0
    
    
    def __init__(self,ip):
        self.ip = ip
        self.port = 8899
        self.rshd = -1
        self.connected = False

def main():
    
    ip = "192.168.19.129"
    port = "8899"
    
    start_time = time.perf_counter()
    
    libpyauboi5.move_joint()







if __name__ == '__main__':
    try:
        import libpyauboi5
    
    except ImportError as e:
        logging.error(f"Failed to import aubo: {e}")
        sys.exit(1)
    main()