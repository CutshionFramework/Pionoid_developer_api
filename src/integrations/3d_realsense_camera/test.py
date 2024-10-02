# import cv2
# import pyrealsense2 as rs
# import math
# import numpy as np

# from datetime import datetime, timezone

# class intelrealsense:
#     #create a method for calculating the z,x,y distance
#     def distance(self, x, y, z):
#         return (x**2 + y**2 + z**2)**0.5
    
#     #create a method for calculating the angle
#     def angle(self, x, y):
#         return math.atan2(y, x) * 180 / math.pi
    
#     #create a method for calculating the distance between two points
#     def distance_between_points(self, x1, y1, x2, y2):
#         return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
#     #crate a method por putting rgb color based on distance 
#     def colorize(self, depth):
#         #create a color map
#         color_map = cv2.applyColorMap(cv2.convertScaleAbs(depth, alpha=0.03), cv2.COLORMAP_JET)
#         return color_map
    
    
#     #create a method to use 2 cameras and callibrate them
#     def callibrate(self):
#         #create a pipeline
#         pipeline = rs.pipeline()
#         #create a config
#         config = rs.config()
#         #create a pipeline profile
#         profile = pipeline.start(config)
#         #create a depth sensor
#         depth_sensor = profile.get_device().first_depth_sensor()
#         #create a depth scale
#         depth_scale = depth_sensor.get_depth_scale()
#         #create a clipping distance
#         clipping_distance_in_meters = 1
#         clipping_distance = clipping_distance_in_meters / depth_scale
#         #create a align object
#         align_to = rs.stream.color
#         align = rs.align(align_to)
#         return pipeline, align, clipping_distance
    

# def main():
#     # 인스턴스 생성
#     irs = intelrealsense()
    
#     # RealSense 설정
#     pipeline = rs.pipeline()
#     config = rs.config()
    
#     # 스트림 설정: 깊이 스트림 활성화
#     config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    
#     # 파이프라인 시작
#     pipeline.start(config)
    
#     try:
#         while True:
#             # 프레임 가져오기
#             frames = pipeline.wait_for_frames()
#             depth_frame = frames.get_depth_frame()
            
#             if not depth_frame:
#                 continue
            
#             # 프레임을 numpy 배열로 변환
#             depth_image = np.asanyarray(depth_frame.get_data())
            
#             # 중앙 점의 z축 거리 측정
#             h, w = depth_image.shape
#             center_x, center_y = w // 2, h // 2
#             z_value = depth_frame.get_distance(center_x, center_y)
            
#             # z축을 포함한 거리 계산
#             dist = irs.distance(center_x, center_y, z_value)
#             print(f"Distance from center (0,0,0): {dist:.2f} meters")
            
#             # 중앙에서 특정 점과의 각도 계산
#             angle = irs.angle(center_x, center_y)
#             print(f"Angle: {angle:.2f} degrees")
            
#             # 두 점 사이의 거리 계산 (중앙과 임의의 점)
#             point_x, point_y = 100, 200  # 임의의 점 (좌표)
#             dist_between_points = irs.distance_between_points(center_x, center_y, point_x, point_y)
#             print(f"Distance between two points: {dist_between_points:.2f} pixels")
            
#             # 깊이 데이터를 기반으로 색상화
#             colorized_depth = irs.colorize(depth_image)
            
#             # 결과 표시
#             cv2.imshow('Depth Image', colorized_depth)
            
#             # ESC 키로 종료
#             if cv2.waitKey(1) & 0xFF == 27:
#                 break

#     finally:
#         # 파이프라인 중지
#         pipeline.stop()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()

import cv2
import pyrealsense2 as rs
import numpy as np
import math

class IntelRealsense:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.pipeline.start(self.config)
        
    # Z, X, Y 거리 계산
    def distance(self, x, y, z):
        return (x**2 + y**2 + z**2)**0.5
    
    # X, Y 각도 계산
    def angle(self, x, y):
        return math.atan2(y, x) * 180 / math.pi
    
    # 두 점 사이의 거리 계산
    def distance_between_points(self, x1, y1, x2, y2):
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
    # 깊이 데이터를 컬러맵으로 변환
    def colorize(self, depth):
        color_map = cv2.applyColorMap(cv2.convertScaleAbs(depth, alpha=0.03), cv2.COLORMAP_JET)
        return color_map
    
# 마우스 이벤트 콜백 함수
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # 마우스 왼쪽 버튼 클릭 시
        depth_frame = param['depth_frame']
        realsense = param['realsense']
        
        # 이미지 크기 가져오기
        depth_width, depth_height = depth_frame.get_width(), depth_frame.get_height()
        
        # 좌표가 유효한 범위 내에 있는지 확인
        if 0 <= x < depth_width and 0 <= y < depth_height:
            # 유효한 범위일 경우 깊이 정보와 각도 계산
            depth = depth_frame.get_distance(x, y)
            angle = realsense.angle(x, y)
            distance_from_center = realsense.distance(x, y, depth)
            
            print(f"Clicked point: ({x}, {y})")
            print(f"Angle: {angle:.2f} degrees")
            print(f"Distance from center: {distance_from_center:.2f} meters")
            print(f"Depth at clicked point: {depth:.2f} meters")
        else:
            print(f"Clicked point ({x}, {y}) is out of range. Valid range: (0, 0) to ({depth_width-1}, {depth_height-1})")

def main():
    # IntelRealsense 클래스 초기화
    realsense = IntelRealsense()
    
    # 윈도우 이름 정의
    window_name = 'RealSense Viewer'
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    
    while True:
        # 프레임 가져오기
        frames = realsense.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        
        if not depth_frame or not color_frame:
            continue
        
        # 프레임을 Numpy 배열로 변환
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        # 깊이 데이터를 컬러맵으로 변환
        colorized_depth = realsense.colorize(depth_image)
        
        # color_image와 colorized_depth의 크기 맞추기
        colorized_depth_resized = cv2.resize(colorized_depth, (color_image.shape[1], color_image.shape[0]))
        
        # 컬러 이미지와 깊이 이미지 나란히 표시
        images = np.hstack((color_image, colorized_depth_resized))
        
        # 마우스 콜백 함수 설정
        cv2.setMouseCallback(window_name, mouse_callback, param={'realsense': realsense, 'depth_frame': depth_frame})
        
        # 이미지 출력
        cv2.imshow(window_name, images)
        
        # ESC 키를 누르면 종료
        if cv2.waitKey(1) == 27:
            break
    
    realsense.pipeline.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

