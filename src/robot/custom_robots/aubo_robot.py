#! /usr/bin/env python
# coding=utf-8
import time

import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import Process, Queue
import os
from math import pi
import sys

# # Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
# print(current_dir)
Dll_path = os.path.join(current_dir, '..', '..', '..', 'Dlls')
# print(Dll_path)
sys.path.append(Dll_path)

try:
    import libpyauboi5
    
except ImportError as e:
    logging.error(f"Failed to import aubo: {e}")
    sys.exit(1)

# 创建一个logger
#logger = logging.getLogger()
logger = logging.getLogger('main.robotcontrol')

# Add the directory containing core_robot to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core_robot import core_robot



def logger_init():
    # 로그 레벨 총 스위치 설정
    logger.setLevel(logging.INFO)

    # 로그 디렉터리 생성
    if not os.path.exists('./logfiles'):
        os.mkdir('./logfiles')

    # 로그 파일에 기록하기 위한 핸들러 생성
    logfile = './logfiles/robot-ctl-python.log'

    # append 모드로 로그 파일 열기
    # fh = logging.FileHandler(logfile, mode='a')
    fh = RotatingFileHandler(logfile, mode='a', maxBytes=1024*1024*50, backupCount=30)

    # 파일 출력에 대한 로그 레벨 스위치 설정
    fh.setLevel(logging.INFO)

    # 콘솔에 출력하기 위한 또 다른 핸들러 생성
    ch = logging.StreamHandler()

    # 콘솔 출력에 대한 로그 레벨 스위치 설정
    ch.setLevel(logging.INFO)

    # 핸들러의 출력 형식 정의
    # formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    formatter = logging.Formatter("%(asctime)s [%(thread)u] %(levelname)s: %(message)s")

    # 파일 출력에 대한 형식 설정
    fh.setFormatter(formatter)

    # 콘솔 출력에 대한 형식 설정
    ch.setFormatter(formatter)

    # 파일 출력을 logger에 설정
    logger.addHandler(fh)

    # 콘솔 출력을 logger에 설정
    logger.addHandler(ch)


class RobotEventType:
    RobotEvent_armCanbusError = 0  # 로봇 팔 CAN 버스 오류
    RobotEvent_remoteHalt = 1  # 로봇 팔 정지
    RobotEvent_remoteEmergencyStop = 2  # 로봇 팔 원격 비상 정지
    RobotEvent_jointError = 3  # 관절 오류
    RobotEvent_forceControl = 4  # 힘 제어
    RobotEvent_exitForceControl = 5  # 힘 제어 종료
    RobotEvent_softEmergency = 6  # 소프트 비상 정지
    RobotEvent_exitSoftEmergency = 7  # 소프트 비상 정지 해제
    RobotEvent_collision = 8  # 충돌
    RobotEvent_collisionStatusChanged = 9  # 충돌 상태 변경
    RobotEvent_tcpParametersSucc = 10  # 도구 동역학 파라미터 설정 성공
    RobotEvent_powerChanged = 11  # 로봇 팔 전원 스위치 상태 변경
    RobotEvent_ArmPowerOff = 12  # 로봇 팔 전원 꺼짐
    RobotEvent_mountingPoseChanged = 13  # 장착 위치 변경
    RobotEvent_encoderError = 14  # 인코더 오류
    RobotEvent_encoderLinesError = 15  # 인코더 라인 수 불일치
    RobotEvent_singularityOverspeed = 16  # 특이점 초과 속도
    RobotEvent_currentAlarm = 17  # 로봇 팔 전류 이상
    RobotEvent_toolioError = 18  # 로봇 팔 도구 I/O 오류
    RobotEvent_robotStartupPhase = 19  # 로봇 팔 시작 단계
    RobotEvent_robotStartupDoneResult = 20  # 로봇 팔 시작 완료 결과
    RobotEvent_robotShutdownDone = 21  # 로봇 팔 종료 결과
    RobotEvent_atTrackTargetPos = 22  # 로봇 팔 궤적 이동 완료 신호
    RobotEvent_SetPowerOnDone = 23  # 전원 설정 완료
    RobotEvent_ReleaseBrakeDone = 24  # 로봇 팔 브레이크 해제 완료
    RobotEvent_robotControllerStateChaned = 25  # 로봇 팔 제어 상태 변경
    RobotEvent_robotControllerError = 26  # 로봇 팔 제어 오류 ---- 주로 알고리즘 문제로 반환됨
    RobotEvent_socketDisconnected = 27  # 소켓 연결 끊김
    RobotEvent_overSpeed = 28  # 초과 속도
    RobotEvent_algorithmException = 29  # 로봇 팔 알고리즘 예외
    RobotEvent_boardIoPoweron = 30  # 외부 전원 신호
    RobotEvent_boardIoRunmode = 31  # 연동/수동 모드
    RobotEvent_boardIoPause = 32  # 외부 일시 정지 신호
    RobotEvent_boardIoStop = 33  # 외부 정지 신호
    RobotEvent_boardIoHalt = 34  # 외부 종료 신호
    RobotEvent_boardIoEmergency = 35  # 외부 비상 정지 신호
    RobotEvent_boardIoRelease_alarm = 36  # 외부 경보 해제 신호
    RobotEvent_boardIoOrigin_pose = 37  # 외부 원점 복귀 신호
    RobotEvent_boardIoAutorun = 38  # 외부 자동 실행 신호
    RobotEvent_safetyIoExternalEmergencyStope = 39  # 외부 비상 정지 입력 01
    RobotEvent_safetyIoExternalSafeguardStope = 40  # 외부 보호 정지 입력 02
    RobotEvent_safetyIoReduced_mode = 41  # 축소 모드 입력
    RobotEvent_safetyIoSafeguard_reset = 42  # 보호 장치 재설정
    RobotEvent_safetyIo3PositionSwitch = 43  # 3단 스위치 1
    RobotEvent_safetyIoOperationalMode = 44  # 작동 모드
    RobotEvent_safetyIoManualEmergencyStop = 45  # 티치 펜던트 비상 정지 01
    RobotEvent_safetyIoSystemStop = 46  # 시스템 정지 입력
    RobotEvent_alreadySuspended = 47  # 로봇 팔 일시 정지
    RobotEvent_alreadyStopped = 48  # 로봇 팔 정지
    RobotEvent_alreadyRunning = 49  # 로봇 팔 실행 중
    RobotEvent_MoveEnterStopState = 1300  # 움직임이 정지 상태로 진입
    RobotEvent_None = 999999  # 이벤트 없음

    # 비오류 이벤트
    NoError = (RobotEvent_forceControl,
            RobotEvent_exitForceControl,
            RobotEvent_tcpParametersSucc,
            RobotEvent_powerChanged,
            RobotEvent_mountingPoseChanged,
            RobotEvent_robotStartupPhase,
            RobotEvent_robotStartupDoneResult,
            RobotEvent_robotShutdownDone,
            RobotEvent_SetPowerOnDone,
            RobotEvent_ReleaseBrakeDone,
            RobotEvent_atTrackTargetPos,
            RobotEvent_robotControllerStateChaned,
            RobotEvent_robotControllerError,
            RobotEvent_algorithmException,
            RobotEvent_alreadyStopped,
            RobotEvent_alreadyRunning,
            RobotEvent_boardIoPoweron,
            RobotEvent_boardIoRunmode,
            RobotEvent_boardIoPause,
            RobotEvent_boardIoStop,
            RobotEvent_boardIoHalt,
            RobotEvent_boardIoRelease_alarm,
            RobotEvent_boardIoOrigin_pose,
            RobotEvent_boardIoAutorun,
            RobotEvent_safetyIoExternalEmergencyStope,
            RobotEvent_safetyIoExternalSafeguardStope,
            RobotEvent_safetyIoReduced_mode,
            RobotEvent_safetyIoSafeguard_reset,
            RobotEvent_safetyIo3PositionSwitch,
            RobotEvent_safetyIoOperationalMode,
            RobotEvent_safetyIoManualEmergencyStop,
            RobotEvent_safetyIoSystemStop,
            RobotEvent_alreadySuspended,
            RobotEvent_alreadyStopped,
            RobotEvent_alreadyRunning,
            RobotEvent_MoveEnterStopState
            )

    # 사용자 게시 이벤트
    UserPostEvent = (RobotEvent_robotControllerError,
                    RobotEvent_safetyIoExternalSafeguardStope,
                    RobotEvent_safetyIoSystemStop
                    )

    # 오류 정리 이벤트
    ClearErrorEvent = (RobotEvent_armCanbusError,
                    RobotEvent_remoteEmergencyStop,
                    RobotEvent_jointError,
                    RobotEvent_collision,
                    RobotEvent_collisionStatusChanged,
                    RobotEvent_encoderError,
                    RobotEvent_encoderLinesError,
                    RobotEvent_currentAlarm,
                    RobotEvent_softEmergency,
                    RobotEvent_exitSoftEmergency
                    )


    def __init__(self):
        pass


class RobotErrorType:
    RobotError_SUCC = 0  # 오류 없음
    RobotError_Base = 2000
    RobotError_RSHD_INIT_FAILED = RobotError_Base + 1  # 라이브러리 초기화 실패
    RobotError_RSHD_UNINIT = RobotError_Base + 2  # 라이브러리 미초기화
    RobotError_NoLink = RobotError_Base + 3  # 연결 없음
    RobotError_Move = RobotError_Base + 4  # 로봇 팔 이동 오류
    RobotError_ControlError = RobotError_Base + RobotEventType.RobotEvent_robotControllerError  # 로봇 팔 제어 오류
    RobotError_LOGIN_FAILED = RobotError_Base + 5  # 로봇 팔 로그인 실패
    RobotError_NotLogin = RobotError_Base + 6  # 로봇 팔 미로그인 상태
    RobotError_ERROR_ARGS = RobotError_Base + 7  # 파라미터 오류


    def __init__(self):
        pass


class RobotEvent:
    def __init__(self, event_type=RobotEventType.RobotEvent_None, event_code=0, event_msg=''):
        self.event_type = event_type
        self.event_code = event_code
        self.event_msg = event_msg


# noinspection SpellCheckingInspection
class RobotError(Exception):
    def __init__(self, error_type=RobotErrorType.RobotError_SUCC, error_code=0, error_msg=''):
        self.error_type = error_type
        self.error_cdoe = error_code
        self.error_msg = error_msg

    def __str__(self):
        return "RobotError type{0} code={1} msg={2}".format(self.error_type, self.error_cdoe, self.error_msg)


class RobotDefaultParameters:
    # 기본 동역학 파라미터
    tool_dynamics = {"position": (0.0, 0.0, 0.0), "payload": 1.0, "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}

    # 기본 충돌 등급
    collision_grade = 6


    def __init__(self):
        pass

    def __str__(self):
        return "Robot Default parameters, tool_dynamics:{0}, collision_grade:{1}".format(self.tool_dynamics,
                                                                                         self.collision_grade)


class RobotMoveTrackType:
    # 원호
    ARC_CIR = 2
    # 궤적
    CARTESIAN_MOVEP = 3
    # 다음 네 가지 삼차 스플라인 보간 곡선은 시작점과 끝점의 가속도가 불연속적인 상황이 발생하여, 새로운 관절 구동 버전과 적합하지 않음
    # 삼차 스플라인 보간(제어점을 통과), 궤적 실행 시간을 자동으로 최적화하며, 현재 자세 변화는 지원하지 않음
    CARTESIAN_CUBICSPLINE = 4
    # 삼차 균등 B 스플라인 보간(제어점을 통과)의 시간 간격을 설정해야 하며, 현재 자세 변화는 지원하지 않음
    CARTESIAN_UBSPLINEINTP = 5
    # 삼차 스플라인 보간 곡선
    JOINT_CUBICSPLINE = 6
    # 궤적 재생에 사용할 수 있음
    JOINT_UBSPLINEINTP = 7


    def __init__(self):
        pass


class RobotIOType:
    # 제어 캐비닛 IO
    ControlBox_DI = 0
    ControlBox_DO = 1
    ControlBox_AI = 2
    ControlBox_AO = 3
    # 사용자 IO
    User_DI = 4
    User_DO = 5
    User_AI = 6
    User_AO = 7


    def __init__(self):
        pass


class RobotToolIoName:
    tool_io_0 = "T_DI/O_00"
    tool_io_1 = "T_DI/O_01"
    tool_io_2 = "T_DI/O_02"
    tool_io_3 = "T_DI/O_03"

    tool_ai_0 = "T_AI_00"
    tool_ai_1 = "T_AI_01"

    def __init__(self):
        pass


class RobotUserIoName:
    # 제어 캐비닛 사용자 DI
    user_di_00 = "U_DI_00"
    user_di_01 = "U_DI_01"
    user_di_02 = "U_DI_02"
    user_di_03 = "U_DI_03"
    user_di_04 = "U_DI_04"
    user_di_05 = "U_DI_05"
    user_di_06 = "U_DI_06"
    user_di_07 = "U_DI_07"
    user_di_10 = "U_DI_10"
    user_di_11 = "U_DI_11"
    user_di_12 = "U_DI_12"
    user_di_13 = "U_DI_13"
    user_di_14 = "U_DI_14"
    user_di_15 = "U_DI_15"
    user_di_16 = "U_DI_16"
    user_di_17 = "U_DI_17"

    # 제어 캐비닛 사용자 DO
    user_do_00 = "U_DO_00"
    user_do_01 = "U_DO_01"
    user_do_02 = "U_DO_02"
    user_do_03 = "U_DO_03"
    user_do_04 = "U_DO_04"
    user_do_05 = "U_DO_05"
    user_do_06 = "U_DO_06"
    user_do_07 = "U_DO_07"
    user_do_10 = "U_DO_10"
    user_do_11 = "U_DO_11"
    user_do_12 = "U_DO_12"
    user_do_13 = "U_DO_13"
    user_do_14 = "U_DO_14"
    user_do_15 = "U_DO_15"
    user_do_16 = "U_DO_16"
    user_do_17 = "U_DO_17"

    # 제어 캐비닛 아날로그 IO
    user_ai_00 = "VI0"
    user_ai_01 = "VI1"
    user_ai_02 = "VI2"
    user_ai_03 = "VI3"

    user_ao_00 = "VO0"
    user_ao_01 = "VO1"
    user_ao_02 = "VO2"
    user_ao_03 = "VO3"


    def __init__(self):
        pass


class RobotStatus:
    # 로봇팔 현재 정지
    Stopped = 0
    # 로봇팔 현재 실행 중
    Running = 1
    # 로봇팔 현재 일시 정지
    Paused = 2
    # 로봇팔 현재 복구
    Resumed = 3


    def __init__(self):
        pass


class RobotRunningMode:
    # 로봇팔 시뮬레이션 모드
    RobotModeSimulator = 0
    # 로봇팔 실제 모드
    RobotModeReal = 1


    def __init__(self):
        pass


class RobotToolPowerType:
    OUT_0V = 0
    OUT_12V = 1
    OUT_24V = 2

    def __init__(self):
        pass


class RobotToolIoAddr:
    TOOL_DIGITAL_IO_0 = 0
    TOOL_DIGITAL_IO_1 = 1
    TOOL_DIGITAL_IO_2 = 2
    TOOL_DIGITAL_IO_3 = 3

    def __init__(self):
        pass


class RobotCoordType:
    # 베이스 좌표계
    Robot_Base_Coordinate = 0
    # 끝단 좌표계
    Robot_End_Coordinate = 1
    # 사용자 좌표계
    Robot_World_Coordinate = 2


    def __init__(self):
        pass


class RobotCoordCalMethod:
    CoordCalMethod_xOy = 0
    CoordCalMethod_yOz = 1
    CoordCalMethod_zOx = 2
    CoordCalMethod_xOxy = 3
    CoordCalMethod_xOxz = 4
    CoordCalMethod_yOyx = 5
    CoordCalMethod_yOyz = 6
    CoordCalMethod_zOzx = 7
    CoordCalMethod_zOzy = 8

    def __init__(self):
        pass


class RobotToolDigitalIoDir:
   # 입력
    IO_IN = 0
    # 출력
    IO_OUT = 1


    def __init__(self):
        pass


class AuboRobot(core_robot):
    # 클라이언트 수
    __client_count = 0

    def __init__(self,ip):
        super().__init__()
        self.ip = ip
        self.port = 8899
        self.rshd = -1
        self.connected = False
        self.last_error = RobotError()
        self.last_event = RobotEvent()
        self.atTrackTargetPos = False
        AuboRobot.__client_count += 1
    
    def login(self, ip, port=8899):
        """
        * 함수: connect
        * 설명: 로봇 서버에 연결
        * 입력: ip 로봇 서버 주소
        *         port 포트 번호
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *         실패 시 기타 값 반환
        * 비고:
        """
        
        logger.info("ip={0}, port={1}".format(ip, port))
        if self.rshd >= 0:
            if not self.connected:
                if libpyauboi5.login(self.rshd, ip, port) == 0:
                    self.connected = True
                    time.sleep(0.5)
                    return RobotErrorType.RobotError_SUCC
                else:
                    logger.error("login failed!")
                    return RobotErrorType.RobotError_LOGIN_FAILED
            else:
                logger.info("already connected.")
                return RobotErrorType.RobotError_SUCC
        else:
            logger.error("RSHD uninitialized!!!")
            return RobotErrorType.RobotError_RSHD_UNINIT
        
    def logout(self):
        """
        * 함수: disconnect
        * 설명: 로봇 서버 연결 해제
        * 입력:
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *         실패 시 기타 값 반환
        * 비고:
        """
        if self.rshd >= 0 and self.connected:
            libpyauboi5.logout(self.rshd)
            self.connected = False
            time.sleep(0.5)
            return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin
    
    def power_on(self, collision=RobotDefaultParameters.collision_grade,
                    tool_dynamics=RobotDefaultParameters.tool_dynamics):
        """
        * 함수: robot_startup
        * 설명: 로봇 시작
        * 입력: collision：충돌 등급 범위(0~10) 기본값: 6
        *         tool_dynamics: 동력학 매개변수
        *         tool_dynamics = 위치, 단위(m)：{"position": (0.0, 0.0, 0.0),
        *                       하중, 단위(kg)： "payload": 1.0,
        *                       관성：           "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *         실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.robot_startup(self.rshd, collision, tool_dynamics)
            time.sleep(0.5)
            return result
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin
    
    def power_off(self):
        """
        * 함수: robot_shutdown
        * 설명: 로봇 종료
        * 입력:
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *         실패 시 기타 값 반환
        * 비고:
        """
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.robot_shutdown(self.rshd)
            time.sleep(0.5)
            return result
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin
    
    def enable_robot(self):
        libpyauboi5.enable_robot()
        
    def disable_robot(self):
        libpyauboi5.disable_robot()
        
    def joint_move(self, joint_pos=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000), issync=True):
        """
        * 함수: move_joint
        * 설명: 로봇 팔 관절 이동
        * 입력: joint_radian: 여섯 개 관절의 각도, 단위(rad)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.move_joint(self.rshd, joint_pos, issync)
            if result != RobotErrorType.RobotError_SUCC:
                self.raise_error(RobotErrorType.RobotError_Move, result, "이동 오류")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin
    
    def linear_move(self, joint_pos=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * 함수: move_line
        * 설명: 로봇 팔이 현재 자세를 유지하며 직선 이동
        * 입력: joint_radian: 여섯 개 관절의 각도, 단위(rad)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.move_line(self.rshd, joint_pos)
            if result != RobotErrorType.RobotError_SUCC:
                self.raise_error(RobotErrorType.RobotError_Move, result, "이동 오류")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin
    
    def get_joint_position(self):
        """
        * 함수: get_joint_status
        * 설명: 현재 로봇팔 상태 정보 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시: 여섯 개의 관절 상태 반환, 포함: 전류, 전압, 온도
        *       {'joint1': {'current': 전류(밀리암페어), 'voltage': 전압(볼트), 'temperature': 온도(섭씨도)},
        *        'joint2': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *        'joint3': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *        'joint4': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *        'joint5': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *        'joint6': {'current': 0, 'voltage': 0.0, 'temperature': 0}}
        *
        *        실패 시: None
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_joint_status(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None
      
    def get_robot_state(self):
        """
        * 함수: get_robot_state
        * 설명: 현재 로봇팔 상태 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시: 로봇팔의 현재 상태
        *       로봇팔이 멈춤 상태: RobotStatus.Stopped
        *       로봇팔이 작동 중: RobotStatus.Running
        *       로봇팔이 일시정지: RobotStatus.Paused
        *       로봇팔이 재개됨: RobotStatus.Resumed
        *
        *       실패 시: None
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_robot_state(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None
    
    def get_robot_status(self):
        """
        * 함수: get_robot_state
        * 설명: 현재 로봇팔 상태 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시: 로봇팔의 현재 상태
        *       로봇팔이 멈춤 상태: RobotStatus.Stopped
        *       로봇팔이 작동 중: RobotStatus.Running
        *       로봇팔이 일시정지: RobotStatus.Paused
        *       로봇팔이 재개됨: RobotStatus.Resumed
        *
        *       실패 시: None
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_robot_state(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None
   
    def get_tcp_position(self):
        """
        * 함수: get_current_waypoint
        * 설명: 현재 로봇팔 위치 정보 가져오기
        * 입력: grade 충돌 등급: 충돌 등급 범위(0~10)
        * 출력:
        * 반환: 성공 시: 관절 위치 정보, 자세한 정보는 비고 참조
        *      실패 시: None
        *
        * 비고: 여섯 개의 관절 각도 {'joint': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        *       위치 'pos': [-0.06403157614989634, -0.4185973810159096, 0.816883228463401],
        *       자세 'ori': [-0.11863209307193756, 0.3820514380931854, 0.0, 0.9164950251579285]}
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_current_waypoint(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def get_all_IO(self):
        all_IO = {
            "CABINET": {
                "dout": [],  # cabinet digital output
                "din": [],   # cabinet digital input
                "aout": [],  # cabinet analog output
                "ain": []    # cabinet analog input
            },
            "TOOL": {
                "tio_dout": [],  # tool digital output
                "tio_din": [],   # tool digital input
                "tio_ain": []    # tool analog input
            },
            "EXTEND": {
                "extio": [],  # external extension IO
                "out": [],
                "in": [], 
            }
        }

        ret = self.get_robot_status()
        
        all_IO["CABINET"]["dout"].append(ret[1][10])
        all_IO["CABINET"]["din"].append(ret[1][11])
        all_IO["CABINET"]["aout"].append(ret[1][12])
        all_IO["CABINET"]["ain"].append(ret[1][13])
        all_IO["TOOL"]["tio_dout"].append(ret[1][14])
        all_IO["TOOL"]["tio_din"].append(ret[1][15])
        all_IO["TOOL"]["tio_ain"].append(ret[1][16])
        all_IO["EXTEND"]["extio"].append(ret[1][17])
        
        return all_IO
    
    def set_digital_output(self, io_type, index, value):
        libpyauboi5.set_digital_output()

# ------------------------------------ other functions --------------------------------------------------  

    def __del__(self):
        AuboRobot.__client_count -= 1
        self.uninitialize()
        logger.info("client_count={0}".format(AuboRobot.__client_count))

    def __str__(self):
        return "RSHD={0}, connected={1}".format(self.rshd, self.connected)

    @staticmethod
    def get_local_time():
        """
        * 함수: get_local_time
        * 설명: 시스템의 현재 시간을 가져옴
        * 입력: 없음
        * 출력:
        * 반환: 시스템 현재 시간 문자열 반환
        * 비고:
        """
        return time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time()))

    def robot_event_callback(self, event):
        """
        * 함수: robot_event_callback
        * 설명: 로봇 이벤트 처리
        * 입력: 없음
        * 출력:
        * 반환: 시스템 이벤트 콜백 함수
        * 비고:
        """
        print("event={0}".format(event))
        if event['type'] not in RobotEventType.NoError:
            self.last_error = RobotError(event['type'], event['code'], event['content'])
        else:
            self.last_event = RobotEvent(event['type'], event['code'], event['content'])
    @staticmethod
    def raise_error(error_type, error_code, error_msg):
        """
        * 함수: raise_error
        * 설명: 예외 이벤트 발생
        * 입력: 없음
        * 출력:
        * 반환: 없음
        * 비고:
        """
        raise RobotError(error_type, error_code, error_msg)

    def check_event(self):
        """
        * 함수: check_event
        * 설명: 로봇에 예외 이벤트가 발생했는지 확인
        * 입력: input
        * 출력: output
        * 반환: void
        * 비고: 예외 이벤트가 발생한 경우 함수에서 예외 이벤트를 발생시킴
        """
        if self.last_error.error_type != RobotErrorType.RobotError_SUCC:
            raise self.last_error
        if self.rshd == -1 or not self.connected:
            self.raise_error(RobotErrorType.RobotError_NoLink, 0, "no socket link")

    @staticmethod
    def initialize():
        """
        * 함수: initialize
        * 설명: 로봇 제어 라이브러리 초기화
        * 입력:
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *         실패 시 기타 값 반환
        * 비고:
        """
        result = libpyauboi5.initialize()
        if result == RobotErrorType.RobotError_SUCC:
            return RobotErrorType.RobotError_SUCC
        else:
            return RobotErrorType.RobotError_RSHD_INIT_FAILED

    @staticmethod
    def uninitialize():
        """
        * 함수: uninitialize
        * 설명: 로봇 제어 라이브러리 해제
        * 입력: input
        * 출력: output
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *         실패 시 기타 값 반환
        * 비고:
        """
        return libpyauboi5.uninitialize()

    def create_context(self):
        """
        * 함수: create_context
        * 설명: 로봇 제어 컨텍스트 핸들 생성
        * 입력:
        * 출력:
        * 반환: 성공 시 RSHD 반환
        * 비고:
        """
        self.rshd = libpyauboi5.create_context()
        return self.rshd

    def get_context(self):
        """
        * 함수: get_context
        * 설명: 로봇의 현재 제어 컨텍스트 가져오기
        * 입력:
        * 출력:
        * 반환: 컨텍스트 핸들 RSHD 반환
        * 비고:
        """
        return self.rshd

    def enable_robot_event(self):
        self.check_event()
        if self.rshd >= 0 and self.connected:
            self.set_robot_event_callback(self.robot_event_callback)
            return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def init_profile(self):
        """
        * 함수: init_profile
        * 설명: 로봇 제어의 전역 속성 초기화
        * 입력:
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        *
        * 비고: 성공적으로 호출되면, 시스템은 이전에 설정된 사용자 좌표계,
        *        속도, 가속도 등의 속성을 자동으로 정리합니다.
        """
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.init_global_move_profile(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_joint_maxacc(self, joint_maxacc=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)):
        """
        * 함수: set_joint_maxacc
        * 설명: 여섯 개 관절의 최대 가속도 설정
        * 입력: joint_maxacc: 여섯 개 관절의 최대 가속도, 단위(rad/s)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_joint_maxacc(self.rshd, joint_maxacc)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_joint_maxacc(self):
        """
        * 함수: get_joint_maxacc
        * 설명: 여섯 개 관절의 최대 가속도 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시 여섯 개 관절의 최대 가속도 반환, 단위(rad/s^2)
        *        실패 시 None 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_joint_maxacc(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def set_joint_maxvelc(self, joint_maxvelc=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)):
        """
        * 함수: set_joint_maxvelc
        * 설명: 여섯 개 관절의 최대 속도 설정
        * 입력: joint_maxvelc: 여섯 개 관절의 최대 속도, 단위(rad/s)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_joint_maxvelc(self.rshd, joint_maxvelc)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_joint_maxvelc(self):
        """
        * 함수: get_joint_maxvelc
        * 설명: 여섯 개 관절의 최대 속도 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시 여섯 개 관절의 최대 속도 반환, 단위(rad/s)
        *        실패 시 None 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_joint_maxvelc(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def set_end_max_line_acc(self, end_maxacc=0.1):
        """
        * 함수: set_end_max_line_acc
        * 설명: 로봇 끝의 최대 선형 가속도 설정
        * 입력: end_maxacc: 로봇 끝의 최대 선형 가속도, 단위(m/s^2)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_line_acc(self.rshd, end_maxacc)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_line_acc(self):
        """
        * 함수: get_end_max_line_acc
        * 설명: 로봇 끝의 최대 선형 가속도 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시 로봇 끝의 최대 가속도 반환, 단위(m/s^2)
        *        실패 시 None 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_line_acc(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def set_end_max_line_velc(self, end_maxvelc=0.1):
        """
        * 함수: set_end_max_line_velc
        * 설명: 로봇 끝의 최대 선형 속도 설정
        * 입력: end_maxacc: 로봇 끝의 최대 선형 속도, 단위(m/s)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_line_velc(self.rshd, end_maxvelc)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_line_velc(self):
        """
        * 함수: get_end_max_line_velc
        * 설명: 로봇 끝의 최대 선형 속도 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시 로봇 끝의 최대 속도 반환, 단위(m/s)
        *        실패 시 None 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_line_velc(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def set_end_max_angle_acc(self, end_maxacc=0.1):
        """
        * 함수: set_end_max_angle_acc
        * 설명: 로봇 끝의 최대 각 가속도 설정
        * 입력: end_maxacc: 로봇 끝의 최대 가속도, 단위(rad/s^2)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_angle_acc(self.rshd, end_maxacc)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_angle_acc(self):
        """
        * 함수: get_end_max_angle_acc
        * 설명: 로봇 끝의 최대 각 가속도 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시 로봇 끝의 최대 각 가속도 반환, 단위(rad/s^2)
        *        실패 시 None 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_angle_acc(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def set_end_max_angle_velc(self, end_maxvelc=0.1):
        """
        * 함수: set_end_max_angle_velc
        * 설명: 로봇 끝의 최대 각 속도 설정
        * 입력: end_maxacc: 로봇 끝의 최대 속도, 단위(rad/s)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_line_velc(self.rshd, end_maxvelc)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_angle_velc(self):
        """
        * 함수: get_end_max_angle_velc
        * 설명: 로봇 끝의 최대 각 속도 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시 로봇 끝의 최대 속도 반환, 단위(rad/s)
        *        실패 시 None 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_line_velc(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def move_to_target_in_cartesian(self, pos, rpy_xyz):
        """
        * 함수: move_to_target_in_cartesian
        * 설명: 데카르트 좌표와 오일러 각을 입력하여 로봇 팔을 목표 위치와 자세로 이동
        * 입력: pos: 위치 좌표(x, y, z), 단위(m)
        *        rpy: 오일러 각(rx, ry, rz), 단위(도)
        * 출력:
        * 반환: 성공 시 RobotError.RobotError_SUCC 반환
        *        실패 시 기타 값 반환
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            # 각도를 라디안으로 변환
            rpy_xyz = [i / 180.0 * pi for i in rpy_xyz]
            # 오일러 각을 쿼터니언으로 변환
            ori = libpyauboi5.rpy_to_quaternion(self.rshd, rpy_xyz)

            # 역운동학을 사용하여 관절 각도 계산
            joint_radian = libpyauboi5.get_current_waypoint(self.rshd)

            ik_result = libpyauboi5.inverse_kin(self.rshd, joint_radian['joint'], pos, ori)

            logging.info("ik_result====>{0}".format(ik_result))

            # 목표 위치로 관절 이동
            result = libpyauboi5.move_joint(self.rshd, ik_result["joint"])
            if result != RobotErrorType.RobotError_SUCC:
                self.raise_error(RobotErrorType.RobotError_Move, result, "이동 오류")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_rotate(self, user_coord, rotate_axis, rotate_angle):
        """
        * 함수: move_rotate
        * 설명: 현재 위치를 유지하면서 자세를 변화시켜 회전 운동을 수행합니다.
        * 입력: user_coord: 사용자 좌표계
        *       user_coord = {'coord_type': 2,
        *                      'calibrate_method': 0,
        *                      'calibrate_points':
        *                          {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                           "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                           "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *                      'tool_desc':
        *                          {"pos": (0.0, 0.0, 0.0),
        *                           "ori": (1.0, 0.0, 0.0, 0.0)}
        *                      }
        *       rotate_axis: 회전 축 (x, y, z) 예시: (1, 0, 0)은 Y축을 따라 회전
        *       rotate_angle: 회전 각도 단위 (라디안)
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_rotate(self.rshd, user_coord, rotate_axis, rotate_angle)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def clear_offline_track(self):
        """
        * 함수: clear_offline_track
        * 설명: 서버에서 비온라인 경로 운동 데이터를 지웁니다.
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.clear_offline_track(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def append_offline_track_waypoint(self, waypoints):
        """
        * 함수: append_offline_track_waypoint
        * 설명: 서버에 비온라인 경로 운동의 웨이포인트를 추가합니다.
        * 입력: waypoints: 비온라인 경로 운동의 웨이포인트 튜플(3000개 이하의 웨이포인트 포함 가능), 단위: 라디안
        *       예시: ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *              (0.0, -0.000001, -0.000001, 0.000001, -0.000001, 0.0))
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.append_offline_track_waypoint(self.rshd, waypoints)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def append_offline_track_file(self, track_file):
        """
        * 함수: append_offline_track_file
        * 설명: 서버에 비온라인 경로 운동 웨이포인트 파일을 추가합니다.
        * 입력: 웨이포인트 파일 경로, 각 행에는 여섯 개 관절의 관절각(라디안)이 포함되며, 쉼표로 구분됩니다.
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.append_offline_track_file(self.rshd, track_file)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def startup_offline_track(self):
        """
        * 함수: startup_offline_track
        * 설명: 서버에 비온라인 경로 운동 시작을 알립니다.
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.startup_offline_track(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def stop_offline_track(self):
        """
        * 함수: stop_offline_track
        * 설명: 서버에 비온라인 경로 운동 중지를 알립니다.
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.stop_offline_track(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def enter_tcp2canbus_mode(self):
        """
        * 함수: enter_tcp2canbus_mode
        * 설명: 서버에 TCP2CANBUS 패스스루 모드 진입을 알립니다.
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.enter_tcp2canbus_mode(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def leave_tcp2canbus_mode(self):
        """
        * 함수: leave_tcp2canbus_mode
        * 설명: 서버에 TCP2CANBUS 패스스루 모드 종료를 알립니다.
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.leave_tcp2canbus_mode(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_waypoint_to_canbus(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * 함수: set_waypoint_to_canbus
        * 설명: CANBUS로 웨이포인트 전송
        * 입력: joint_radian: 여섯 개 관절의 관절각, 단위(rad)
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_waypoint_to_canbus(self.rshd, joint_radian)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def remove_all_waypoint(self):
        """
        * 함수: remove_all_waypoint
        * 설명: 설정된 모든 전역 웨이포인트 제거
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.remove_all_waypoint(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def add_waypoint(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * 함수: add_waypoint
        * 설명: 경로 운동을 위한 전역 웨이포인트 추가
        * 입력: joint_radian: 여섯 개 관절의 관절각, 단위(rad)
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.add_waypoint(self.rshd, joint_radian)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_blend_radius(self, blend_radius=0.01):
        """
        * 함수: set_blend_radius
        * 설명: 블렌딩 반경 설정
        * 입력: blend_radius: 블렌딩 반경, 단위(m)
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            if 0.01 >= blend_radius <= 0.05:
                return libpyauboi5.set_blend_radius(self.rshd, blend_radius)
            else:
                logger.warn("블렌딩 반경 값 범위는 0.01~0.05이어야 합니다.")
                return RobotErrorType.RobotError_ERROR_ARGS
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_circular_loop_times(self, circular_count=1):
        """
        * 함수: set_circular_loop_times
        * 설명: 원 운동 횟수 설정
        * 입력: circular_count: 원의 운동 횟수
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고: circular_count가 0보다 클 때 로봇이 원 운동을 circular_count회 수행합니다.
        *       circular_count가 0일 때 로봇은 원호 경로 운동을 수행합니다.
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_circular_loop_times(self.rshd, circular_count)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_user_coord(self, user_coord):
        """
        * 함수: set_user_coord
        * 설명: 사용자 좌표계 설정
        * 입력: user_coord: 사용자 좌표계
        *       user_coord = {'coord_type': RobotCoordType.Robot_World_Coordinate,
        *                    'calibrate_method': RobotCoordCalMethod.CoordCalMethod_xOy,
        *                    'calibrate_points':
        *                        {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                         "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                         "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *                    'tool_desc':
        *                        {"pos": (0.0, 0.0, 0.0),
        *                         "ori": (1.0, 0.0, 0.0, 0.0)}
        *                    }
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_user_coord(self.rshd, user_coord)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_base_coord(self):
        """
        * 함수: set_base_coord
        * 설명: 베이스 좌표계를 설정합니다.
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_base_coord(self.rshd)
        else:
            logger.warn("RSHD가 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def check_user_coord(self, user_coord):
        """
        * 함수: check_user_coord
        * 설명: 사용자 좌표계 파라미터 설정이 적절한지 확인합니다.
        * 입력: user_coord: 사용자 좌표계
        *       user_coord = {'coord_type': 2,
        *        'calibrate_method': 0,
        *        'calibrate_points':
        *            {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *             "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *             "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *        'tool_desc':
        *            {"pos": (0.0, 0.0, 0.0),
        *             "ori": (1.0, 0.0, 0.0, 0.0)}
        *        }
        * 출력:
        * 반환: 적절하면: RobotError.RobotError_SUCC
        *       부적절하면: 기타 값
        * 비고:
        """

        return libpyauboi5.check_user_coord(self.rshd, user_coord)

    def set_relative_offset_on_base(self, relative_pos, relative_ori):
        """
        * 함수: set_relative_offset_on_base
        * 설명: 기본 좌표계에 대한 상대적 이동 오프셋을 설정합니다.
        * 입력: relative_pos=(x, y, z) 상대적 위치 이동, 단위(m)
        *       relative_ori=(w,x,y,z) 상대적 자세
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:            
            return libpyauboi5.set_relative_offset_on_base(self.rshd, relative_pos, relative_ori)
            
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_relative_offset_on_user(self, relative_pos, relative_ori, user_coord):
        """
        * 함수: set_relative_offset_on_user
        * 설명: 사용자 좌표계를 기반으로 한 이동 오프셋을 설정합니다.
        * 입력: relative_pos=(x, y, z) 상대적 위치 이동, 단위(m)
        *       relative_ori=(w,x,y,z) 목표 자세
        *       user_coord: 사용자 좌표계
        *       user_coord = {'coord_type': 2,
        *        'calibrate_method': 0,
        *        'calibrate_points':
        *            {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *             "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *             "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *        'tool_desc':
        *            {"pos": (0.0, 0.0, 0.0),
        *             "ori": (1.0, 0.0, 0.0, 0.0)}
        *        }
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_relative_offset_on_user(self.rshd, relative_pos, relative_ori, user_coord)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_no_arrival_ahead(self):
        """
        * 함수: set_no_arrival_ahead
        * 설명: 사전 도착 설정 취소
        * 입력:
        *
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_no_arrival_ahead(self.rshd)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set no arrival ahead error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_arrival_ahead_distance(self, distance=0.0):
        """
        * 함수: set_arrival_ahead_distance
        * 설명: 거리 모드에서의 사전 도착 거리를 설정
        * 입력: distance 사전 도착 거리, 단위(미터)
        *
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_arrival_ahead_distance(self.rshd, distance)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set arrival ahead distance error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_arrival_ahead_time(self, sec=0.0):
        """
        * 함수: set_arrival_ahead_time
        * 설명: 시간 모드에서의 사전 도착 시간을 설정
        * 입력: sec 사전 도착 시간, 단위(초)
        *
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_arrival_ahead_time(self.rshd, sec)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set arrival ahead time error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_arrival_ahead_blend(self, distance=0.0):
        """
        * 함수: set_arrival_ahead_blend
        * 설명: 거리 모드에서 교차 반경 거리를 설정
        * 입력: blend 교차 반경, 단위(미터)
        *
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_arrival_ahead_blend(self.rshd, distance)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set arrival ahead blend error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_track(self, track):
        """
        * 함수: move_track
        * 설명: 궤적 운동
        * 입력: track 궤적 유형, 아래와 같음:
        *       원호 운동: RobotMoveTrackType.ARC_CIR
        *       궤적 운동: RobotMoveTrackType.CARTESIAN_MOVEP
        *
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타 값
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.move_track(self.rshd, track)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "move error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def forward_kin(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * 함수: forward_kin
        * 설명: 순방향 해석
        * 입력: joint_radian: 여섯 개 관절의 관절 각도, 단위(rad)
        * 출력:
        * 반환: 성공 시: 관절 순방향 해석 결과, 결과는 NOTES 참조
        *       실패 시: None
        *
        * 비고: 여섯 개 관절 각도 {'joint': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        *       위치 'pos': [-0.06403157614989634, -0.4185973810159096, 0.816883228463401],
        *       자세 'ori': [-0.11863209307193756, 0.3820514380931854, 0.0, 0.9164950251579285]}
        """

        if self.rshd >= 0:
            return libpyauboi5.forward_kin(self.rshd, joint_radian)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def inverse_kin(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000),
                    pos=(0.0, 0.0, 0.0), ori=(1.0, 0.0, 0.0, 0.0)):
        """
        * 함수: inverse_kin
        * 설명: 역방향 해석
        * 입력: joint_radian: 시작점 여섯 개 관절의 관절 각도, 단위(rad)
        *       pos 위치(x, y, z) 단위(m)
        *       ori 자세(w, x, y, z)
        * 출력:
        * 반환: 성공 시: 관절 역방향 해석 결과, 결과는 NOTES 참조
        *       실패 시: None
        *
        * 비고: 여섯 개 관절 각도 {'joint': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        *       위치 'pos': [-0.06403157614989634, -0.4185973810159096, 0.816883228463401],
        *       자세 'ori': [-0.11863209307193756, 0.3820514380931854, 0.0, 0.9164950251579285]}
        """

        if self.rshd >= 0:
            return libpyauboi5.inverse_kin(self.rshd, joint_radian, pos, ori)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def base_to_user(self, pos, ori, user_coord, user_tool):
        """
        * 함수: base_to_user
        * 설명: 사용자 좌표계를 기준 좌표계로 변환
        * 입력: pos: 기준 좌표계에서의 위치(x, y, z) 단위(m)
        *       ori: 기준 좌표계에서의 자세(w, x, y, z)
        *       user_coord: 사용자 좌표계
        *       user_coord = {'coord_type': 2,
        *                    'calibrate_method': 0,
        *                    'calibrate_points':
        *                        {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                         "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                         "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *                    'tool_desc':
        *                        {"pos": (0.0, 0.0, 0.0),
        *                         "ori": (1.0, 0.0, 0.0, 0.0)}
        *                    }
        *       user_tool: 사용자 도구 설명
        *       user_tool={"pos": (x, y, z), "ori": (w, x, y, z)}
        * 출력:
        * 반환: 성공 시: 위치와 자세를 반환{"pos": (x, y, z), "ori": (w, x, y, z)}
        *       실패 시: None
        *
        * 비고:
        """

        return libpyauboi5.base_to_user(self.rshd, pos, ori, user_coord, user_tool)

    def user_to_base(self, pos, ori, user_coord, user_tool):
        """
        * 함수: user_to_base
        * 설명: 사용자 좌표계를 기준 좌표계로 변환
        * 입력: pos: 사용자 좌표계에서의 위치(x, y, z) 단위(m)
        *       ori: 사용자 좌표계에서의 자세(w, x, y, z)
        *       user_coord: 사용자 좌표계
        *       user_coord = {'coord_type': 2,
        *                    'calibrate_method': 0,
        *                    'calibrate_points':
        *                        {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                         "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                         "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *                    'tool_desc':
        *                        {"pos": (0.0, 0.0, 0.0),
        *                         "ori": (1.0, 0.0, 0.0, 0.0)}
        *                    }
        *       user_tool: 사용자 도구 설명
        *       user_tool={"pos": (x, y, z), "ori": (w, x, y, z)}
        * 출력:
        * 반환: 성공 시: 위치와 자세를 반환{"pos": (x, y, z), "ori": (w, x, y, z)}
        *       실패 시: None
        *
        * 비고:
        """

        return libpyauboi5.user_to_base(self.rshd, pos, ori, user_coord, user_tool)

    def base_to_base_additional_tool(self, flange_pos, flange_ori, user_tool):
        """
        * 함수: base_to_base_additional_tool
        * 설명: 기준 좌표계를 기준으로 도구 끝점의 위치와 자세를 얻음
        * 입력: pos: 기준 좌표계에 따른 플랜지 중심의 위치 정보(x, y, z) 단위(m)
        *       ori: 기준 좌표계에 따른 자세 정보(w, x, y, z)
        *       user_tool: 사용자 도구 설명
        *       user_tool={"pos": (x, y, z), "ori": (w, x, y, z)}
        * 출력:
        * 반환: 성공 시: 기준 좌표계에 따른 도구 끝점의 위치와 자세 정보{"pos": (x, y, z), "ori": (w, x, y, z)}
        *       실패 시: None
        *
        * 비고:
        """

        return libpyauboi5.base_to_base_additional_tool(self.rshd, flange_pos, flange_ori, user_tool)

    def rpy_to_quaternion(self, rpy):
        """
        * 함수: rpy_to_quaternion
        * 설명: 오일러 각도를 쿼터니언으로 변환
        * 입력: rpy: 오일러 각도(rx, ry, rz), 단위(m)
        * 출력:
        * 반환: 성공 시: 쿼터니언 결과, 자세한 내용은 NOTES 참조
        *       실패 시: None
        *
        * 비고: 쿼터니언(w, x, y, z)
        """

        if self.rshd >= 0:
            return libpyauboi5.rpy_to_quaternion(self.rshd, rpy)
        else:
            logger.warn("RSHD uninitialized !!!")
            return None

    def quaternion_to_rpy(self, ori):
        """
        * 함수: quaternion_to_rpy
        * 설명: 쿼터니언을 오일러 각도로 변환
        * 입력: 쿼터니언(w, x, y, z)
        * 출력:
        * 반환: 성공 시: 오일러 각도 결과, 자세한 내용은 NOTES 참조
        *       실패 시: None
        *
        * 비고: rpy: 오일러 각도(rx, ry, rz), 단위(m)
        """

        if self.rshd >= 0:
            return libpyauboi5.quaternion_to_rpy(self.rshd, ori)
        else:
            logger.warn("RSHD uninitialized !!!")
            return None

    def set_tool_end_param(self, tool_end_param):
        """
        * 함수: set_tool_end_param
        * 설명: 끝단 도구 매개변수 설정
        * 입력: 끝단 도구 매개변수: tool_end_param={"pos": (x, y, z), "ori": (w, x, y, z)}
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        *
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_end_param(self.rshd, tool_end_param)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_none_tool_dynamics_param(self):
        """
        * 함수: set_none_tool_dynamics_param
        * 설명: 도구가 없는 경우의 동역학 매개변수 설정
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        *
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_none_tool_dynamics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_dynamics_param(self, tool_dynamics):
        """
        * 함수: set_tool_end_param
        * 설명: 도구의 동역학 매개변수 설정
        * 입력: tool_dynamics: 운동학 매개변수
        *       tool_dynamics = 위치, 단위(m) ：{"position": (0.0, 0.0, 0.0),
        *                          하중, 단위(kg)： "payload": 1.0,
        *                          관성：          "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        *
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_dynamics_param(self.rshd, tool_dynamics)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_tool_dynamics_param(self):
        """
        * 함수: get_tool_dynamics_param
        * 설명: 끝단 도구의 동역학 매개변수 가져오기
        * 입력:
        * 출력:
        * 반환: 성공 시: 운동학 매개변수
        *       tool_dynamics = 위치, 단위(m) ：{"position": (0.0, 0.0, 0.0),
        *                          하중, 단위(kg)： "payload": 1.0,
        *                          관성：          "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}
        *
        *       실패 시: None
        *
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_dynamics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_none_tool_kinematics_param(self):
        """
        * 함수: set_none_tool_kinematics_param
        * 설명: 도구가 없는 경우의 운동학 매개변수 설정
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        *
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_none_tool_kinematics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_kinematics_param(self, tool_end_param):
        """
        * 함수: set_tool_kinematics_param
        * 설명: 도구의 운동학 매개변수 설정
        * 입력: 끝단 도구 매개변수: tool_end_param={"pos": (x, y, z), "ori": (w, x, y, z)}
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        *
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_kinematics_param(self.rshd, tool_end_param)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_tool_kinematics_param(self):
        """
        * 함수: get_tool_kinematics_param
        * 설명: 도구의 운동학 매개변수 설정
        * 입력:
        * 출력:
        * 반환: 성공 시: 도구의 운동학 매개변수
        *       tool_end_param={"pos": (x, y, z), "ori": (w, x, y, z)}
        *
        *       실패 시: None
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_kinematics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def move_stop(self):
        """
        * 함수: move_stop
        * 설명: 로봇 팔의 움직임을 멈춤
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_stop(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_pause(self):
        """
        * 함수: move_pause
        * 설명: 로봇 팔의 움직임을 일시 중지함
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_pause(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_continue(self):
        """
        * 함수: move_continue
        * 설명: 일시 중지 후 로봇 팔의 움직임을 재개함
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_continue(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def collision_recover(self):
        """
        * 함수: collision_recover
        * 설명: 로봇팔 충돌 후 복구
        * 입력:
        * 출력:
        * 반환:    성공 시: RobotError.RobotError_SUCC
        *          실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.collision_recover(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def enter_reduce_mode(self):
        """
        * 함수: enter_reduce_mode
        * 설명: 로봇팔의 동작을 축소 모드로 설정
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.enter_reduce_mode(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def exit_reduce_mode(self):
        """
        * 함수: exit_reduce_mode
        * 설명: 로봇팔의 동작을 축소 모드에서 벗어나게 설정
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.exit_reduce_mode(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def project_startup(self):
        """
        * 함수: project_startup
        * 설명: 로봇팔 프로젝트 시작을 알리고, 서버는 동시에 안전 IO 감지를 시작
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.project_startup(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def rs_project_stop(self):
        """
        * 함수: rs_project_stop
        * 설명: 로봇팔 프로젝트 종료를 알리고, 서버는 안전 IO 감지를 중단
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.rs_project_stop(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_work_mode(self, mode=0):
        """
        * 함수: set_work_mode
        * 설명: 로봇팔 서버 작업 모드 설정
        * 입력: mode: 서버 작업 모드
        *      로봇팔 시뮬레이션 모드: RobotRunningMode.RobotModeSimulator
        *      로봇팔 실제 모드: RobotRunningMode.RobotModeReal
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_work_mode(self.rshd, mode)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_work_mode(self):
        """
        * 함수: set_work_mode
        * 설명: 로봇팔 서버의 현재 작업 모드 가져오기
        * 입력: mode: 서버 작업 모드
        *      로봇팔 시뮬레이션 모드: RobotRunningMode.RobotModeSimulator
        *      로봇팔 실제 모드: RobotRunningMode.RobotModeReal
        * 출력:
        * 반환: 성공 시: 서버 작업 모드
        *       로봇팔 시뮬레이션 모드: RobotRunningMode.RobotModeSimulator
        *       로봇팔 실제 모드: RobotRunningMode.RobotModeReal
        *
        *       실패 시: None
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_work_mode(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def set_collision_class(self, grade=6):
        """
        * 함수: set_collision_class
        * 설명: 로봇팔 충돌 등급 설정
        * 입력: grade 충돌 등급: 충돌 등급 범위(0~10)
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_collision_class(self.rshd, grade)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def is_have_real_robot(self):
        """
        * 함수: is_have_real_robot
        * 설명: 현재 실제 로봇팔이 연결되어 있는지 확인
        * 입력:
        * 출력:
        * 반환: 성공 시: 1: 존재, 0: 존재하지 않음
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.is_have_real_robot(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def is_online_mode(self):
        """
        * 함수: is_online_mode
        * 설명: 현재 로봇팔이 온라인 모드에서 작동 중인지 확인
        * 입력:
        * 출력:
        * 반환: 성공 시: 1: 온라인, 0: 오프라인
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.is_online_mode(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def is_online_master_mode(self):
        """
        * 함수: is_online_master_mode
        * 설명: 현재 로봇팔이 온라인 주 모드에서 작동 중인지 확인
        * 입력:
        * 출력:
        * 반환: 성공 시: 1: 주 모드, 0: 종 모드
        *       실패 시: 기타
        * 비고:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.is_online_master_mode(self.rshd)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None
    
    def get_board_io_config(self, io_type=RobotIOType.User_DO):
        """
        * 함수: get_board_io_config
        * 설명:
        * 입력: io_type: IO 유형: RobotIOType
        * 출력:
        * 반환: 성공 시: IO 설정
        *       [{"id": ID
        *         "name": "IO 이름"
        *         "addr": IO 주소
        *         "type": IO 유형
        *         "value": IO 현재 값},]
        *
        *       실패 시: None
        * 비고: RobotIOType은 class RobotIOType 참조
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_board_io_config(self.rshd, io_type)
        else:
            logger.warn("RSHD 초기화되지 않았거나 로그인되지 않았습니다!!!")
            return None

    def get_board_io_status(self, io_type, io_name):
        """
        * 함수: get_board_io_status
        * 설명: IO 상태 가져오기
        * 입력: io_type: 유형
        *       io_name: 이름 RobotUserIoName.user_dx_xx
        * 출력:
        * 반환: 성공 시: IO 상태 double 값(디지털 IO는 0 또는 1 반환, 아날로그 IO는 실수 반환)
        *       실패 시: None
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_board_io_status(self.rshd, io_type, io_name)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_board_io_status(self, io_type, io_name, io_value):
        """
        * 함수: set_board_io_status
        * 설명: IO 상태 설정
        * 입력: io_type: 유형
        *       io_name: 이름 RobotUserIoName.user_dx_xx
        *       io_value: 상태 값 (디지털 IO는 0 또는 1 반환, 아날로그 IO는 실수 반환)
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        #self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_board_io_status(self.rshd, io_type, io_name, io_value)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def set_tool_power_type(self, power_type=RobotToolPowerType.OUT_0V):
        """
        * 함수: set_tool_power_type
        * 설명: 도구 단말 전원 유형 설정
        * 입력: power_type: 전원 유형
        *       RobotToolPowerType.OUT_0V
        *       RobotToolPowerType.OUT_12V
        *       RobotToolPowerType.OUT_24V
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_power_type(self.rshd, power_type)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_tool_power_type(self):
        """
        * 함수: get_tool_power_type
        * 설명: 도구 단말 전원 유형 가져오기
        * 입력: power_type: 전원 유형

        * 출력:
        * 반환: 성공 시: 전원 유형, 포함 내용은 다음과 같음:
        *               RobotToolPowerType.OUT_0V
        *               RobotToolPowerType.OUT_12V
        *               RobotToolPowerType.OUT_24V
        *
        *      실패 시: None
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_power_type(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_io_type(self, io_addr=RobotToolIoAddr.TOOL_DIGITAL_IO_0,
                         io_type=RobotToolDigitalIoDir.IO_OUT):
        """
        * 함수: set_tool_io_type
        * 설명: 도구 단말의 디지털 IO 유형 설정
        * 입력: io_addr: 도구 단말 IO 주소, 자세한 내용은 class RobotToolIoAddr 참조
        *       io_type: 도구 단말 IO 유형, 자세한 내용은 class RobotToolDigitalIoDir 참조

        * 출력:
        * 반환: 성공 시: IO 유형, 포함 내용은 다음과 같음:
        *              RobotToolDigitalIoDir.IO_IN
        *              RobotToolDigitalIoDir.IO_OUT
        *
        *       실패 시: None
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_io_type(self.rshd, io_addr, io_type)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_tool_power_voltage(self):
        """
        * 함수: get_tool_power_voltage
        * 설명: 도구 단말의 전압 값을 가져옴
        * 입력:
        * 출력:
        * 반환:    성공 시: 전압 값을 반환, 단위는 (볼트)
        *          실패 시: None
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_power_voltage(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_tool_io_status(self, io_name):
        """
        * 함수: get_tool_io_status
        * 설명: 도구 단말의 IO 상태를 가져옴
        * 입력: io_name: IO 이름

        * 출력:
        * 반환: 성공 시: 도구 단말의 IO 상태를 반환
        *
        *       실패 시: None
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_io_status(self.rshd, io_name)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_io_status(self, io_name, io_status):
        """
        * 함수: set_tool_io_status
        * 설명: 도구 단말의 IO 상태를 설정함
        * 입력: io_name: 도구 단말의 IO 이름
        *       io_status: 도구 단말의 IO 상태 (값 범위: 0 또는 1)

        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_do_status(self.rshd, io_name, io_status)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def startup_excit_traj_track(self, track_file='', track_type=0, subtype=0):
        """
        * 함수: startup_excit_traj_track
        * 설명: 서버에 인식 경로 운동을 시작하도록 알림
        * 입력:
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.startup_excit_traj_track(self.rshd, track_file, track_type, subtype)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_dynidentify_results(self):
        """
        * 함수: get_dynidentify_results
        * 설명: 인식 결과를 가져옴
        * 입력:
        * 출력:
        * 반환:    성공 시: 인식 결과 배열
        *          실패 시: None
        * 비고:
        """

        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_dynidentify_results(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_robot_event_callback(self, callback):
        """
        * 함수: set_robot_event_callback
        * 설명: 로봇 이벤트 콜백 함수를 설정
        * 입력: callback: 콜백 함수 이름
        * 출력:
        * 반환: 성공 시: RobotError.RobotError_SUCC
        *       실패 시: 기타
        * 비고:
        """

        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_robot_event_callback(self.rshd, callback)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

# 测试函数
def test(test_count):
    # Logger 초기화
    logger_init()

    # 테스트 시작 log
    logger.info("{0} 테스트 시작...".format(AuboRobot.get_local_time()))

    # 시스템 초기화
    AuboRobot.initialize()

    # 로봇 컨트롤러 클래스 생성
    robot = AuboRobot()

    # 컨텍스트 생성
    handle = robot.create_context()

    # 컨텍스트 출력
    logger.info("robot.rshd={0}".format(handle))

    try:
        # 서버 연결
        #ip = 'localhost'
        ip = '192.168.19.129'

        port = 8899
        result = robot.login(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("{0}:{1} 서버 연결 실패.".format(ip, port))
        else:
            # # 재전원 연결
            #robot.robot_shutdown()
            #
            # # 전원 연결
            robot.power_on()
            #
            # # 충돌 등급 설정
            robot.set_collision_class(7)

            # 툴 끝부분 전원을 12V로 설정
            # robot.set_tool_power_type(RobotToolPowerType.OUT_12V)

            # 툴 끝부분 IO_0을 출력으로 설정
            #robot.set_tool_io_type(RobotToolIoAddr.TOOL_DIGITAL_IO_0, RobotToolDigitalIoDir.IO_OUT)

            # 툴 끝부분 IO_0 현재 상태 가져오기
            #tool_io_status = robot.get_tool_io_status(RobotToolIoName.tool_io_0)
            #logger.info("tool_io_0={0}".format(tool_io_status))

            # 툴 끝부분 IO_0 상태 설정
            #robot.set_tool_io_status(RobotToolIoName.tool_io_0, 1)

            # 제어 캐비닛의 사용자 DO 가져오기
            #io_config = robot.get_board_io_config(RobotIOType.User_DO)

            # DO 설정 출력
            #logger.info(io_config)

            # 현재 로봇이 온라인 모드로 실행 중인지 여부
            #logger.info("로봇 온라인 모드 상태는 {0}".format(robot.is_online_mode()))

            # 반복 테스트
            while test_count > 0:
                test_count -= 1

                joint_status = robot.get_joint_position()
                logger.info("joint_status={0}".format(joint_status))

                # 전역 설정 파일 초기화
                robot.init_profile()

                # 관절 최대 가속도 설정
                robot.set_joint_maxacc((1.5, 1.5, 1.5, 1.5, 1.5, 1.5))

                # 관절 최대 가속도 설정
                robot.set_joint_maxvelc((1.5, 1.5, 1.5, 1.5, 1.5, 1.5))

                joint_radian = (0.6, 0.4, -0.948709, -0.397018, -1.570800, 0.541673)
                logger.info("관절을 {0} 위치로 이동".format(joint_radian))

                robot.joint_move(joint_radian)

                # 관절 최대 가속도 가져오기
                logger.info(robot.get_joint_maxacc())

                # 순방향 운동학 테스트
                fk_ret = robot.forward_kin((-0.000003, -0.127267, -1.321122, 0.376934, -1.570796, -0.000008))
                logger.info(fk_ret)

                # 역방향 운동학
                joint_radian = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
                ik_result = robot.inverse_kin(joint_radian, fk_ret['pos'], fk_ret['ori'])
                logger.info(ik_result)

                # 관절 움직임 1
                joint_radian = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
                logger.info("관절을 {0} 위치로 이동".format(joint_radian))
                robot.joint_move(joint_radian)

                # 관절 움직임 2
                joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
                logger.info("관절을 {0} 위치로 이동".format(joint_radian))
                robot.joint_move(joint_radian)

                # 관절 움직임 3
                joint_radian = (-0.000003, -0.127267, -1.321122, 0.376934, -1.570796, -0.000008)
                logger.info("관절을 {0} 위치로 이동".format(joint_radian))
                robot.joint_move(joint_radian)

                # 로봇 끝부분 최대 선형 가속도 설정 (m/s)
                robot.set_end_max_line_acc(0.5)

                # 로봇 끝부분 최대 선형 속도 설정 (m/s)
                robot.set_end_max_line_velc(0.2)

                # 설정된 모든 전역 웨이포인트 제거
                robot.remove_all_waypoint()

                # 전역 웨이포인트 1 추가, 궤적 운동을 위해 사용
                joint_radian = (-0.000003, -0.127267, -1.321122, 0.376934, -1.570796, -0.000008)
                robot.add_waypoint(joint_radian)

                # 전역 웨이포인트 2 추가, 궤적 운동을 위해 사용
                joint_radian = (-0.211675, -0.325189, -1.466753, 0.429232, -1.570794, -0.211680)
                robot.add_waypoint(joint_radian)

                # 전역 웨이포인트 3 추가, 궤적 운동을 위해 사용
                joint_radian = (-0.037186, -0.224307, -1.398285, 0.396819, -1.570796, -0.037191)
                robot.add_waypoint(joint_radian)

                # 원 운동 횟수 설정
                robot.set_circular_loop_times(3)

                # 원호 운동
                logger.info("move_track ARC_CIR")
                robot.move_track(RobotMoveTrackType.ARC_CIR)

                # 설정된 모든 전역 웨이포인트 제거
                robot.remove_all_waypoint()

                # 로봇 관절을 0 위치로 이동
                joint_radian = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
                logger.info("관절을 {0} 위치로 이동".format(joint_radian))
                robot.joint_move(joint_radian)

            # 서버 연결 해제
            robot.logout()

    except RobotError as e:
        logger.error("{0} 로봇 이벤트:{1}".format(robot.get_local_time(), e))


    finally:
        # 서버 연결 해제
        if robot.connected:
            # 로봇 종료
            robot.power_off()
            # 로봇 연결 해제
            robot.logout()
        # 라이브러리 자원 해제
        Auboi5Robot.uninitialize()
        logger.info("{0} 테스트 완료.".format(Auboi5Robot.get_local_time()))  

def step_test():
    # 로거 초기화
    logger_init()

    # 테스트 시작
    logger.info("{0} 테스트 시작 중...".format(Auboi5Robot.get_local_time()))

    # 시스템 초기화
    Auboi5Robot.initialize()

    # 로봇 제어 클래스 생성
    robot = Auboi5Robot()

    # 컨텍스트 생성
    handle = robot.create_context()

    # 컨텍스트 출력
    logger.info("robot.rshd={0}".format(handle))

    try:

        # 서버에 연결
        ip = '192.168.19.129'
        port = 8899
        result = robot.login(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("서버 {0}:{1}에 연결 실패.".format(ip, port))
        else:
            # 전원 꺼짐
            robot.power_off()

            # 전원 켜짐
            robot.power_on()

            # 충돌 등급 설정
            robot.set_collision_class(7)

            # # 전역 구성 파일 초기화
            # robot.init_profile()
            #
            # # logger.info(robot.get_board_io_config(RobotIOType.User_DI))
            #
            # # 현재 위치 가져오기
            # logger.info(robot.get_current_waypoint())
            #
            # joint_radian = (0, 0, 0, 0, 0, 0)
            # # 축을 초기 위치로 이동
            # robot.move_joint(joint_radian)
            #
            # # Z축을 따라 0.1밀리미터 이동
            # current_pos = robot.get_current_waypoint()
            #
            # current_pos['pos'][2] -= 0.001
            #
            # ik_result = robot.inverse_kin(current_pos['joint'], current_pos['pos'], current_pos['ori'])
            # logger.info(ik_result)
            #
            # # joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
            # # logger.info("관절을 {0}으로 이동".format(joint_radian))
            # # robot.move_joint(joint_radian)
            #
            # robot.move_line(ik_result['joint'])

            # 서버 연결 해제
            robot.logout()

    except RobotError as e:
        logger.error("로봇 이벤트:{0}".format(e))

    finally:
        # 서버 연결 해제
        if robot.connected:
            # 로봇 연결 해제
            robot.logout()
        # 라이브러리 리소스 해제
        Auboi5Robot.uninitialize()
        logger.info("{0} 테스트 완료.".format(Auboi5Robot.get_local_time()))

def excit_traj_track_test():
    # 로거 초기화
    logger_init()

    # 테스트 시작
    logger.info("{0} 테스트 시작 중...".format(Auboi5Robot.get_local_time()))

    # 시스템 초기화
    Auboi5Robot.initialize()

    # 로봇 제어 클래스 생성
    robot = Auboi5Robot()

    # 컨텍스트 생성
    handle = robot.create_context()

    # 컨텍스트 출력
    logger.info("robot.rshd={0}".format(handle))

    try:

        # 서버에 연결
        ip = '192.168.19.129'
        port = 8899
        result = robot.login(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("서버 {0}:{1}에 연결 실패.".format(ip, port))
        else:

            # 전원 재부팅
            # robot.robot_shutdown()

            # 전원 켜짐
            # robot.robot_startup()

            # 충돌 등급 설정
            # robot.set_collision_class(7)

            joint_radian = (0, 0, 0, 0, 0, 0)
            # 축을 초기 위치로 이동
            robot.joint_move(joint_radian)

            logger.info("excitation trajectory 트랙 시작 중....")

            # 식별 궤적 시작
            #robot.startup_excit_traj_track("dynamics_exciting_trajectories/excitTraj1.offt", 1, 0)

            # 2초 대기 후 식별 결과 확인
            #time.sleep(5)

            # 식별 결과 가져오기
            dynidentify_ret = robot.get_dynidentify_results()
            logger.info("식별 결과={0}".format(dynidentify_ret))
            for i in range(0,54):
                dynidentify_ret[i] = dynidentify_ret[i]/1024.0
            logger.info("식별 결과={0}".format(dynidentify_ret))

            # 서버 연결 해제
            robot.logout()

    except RobotError as e:
        logger.error("로봇 이벤트:{0}".format(e))


    finally:
        # 서버 연결 해제
        if robot.connected:
            # 로봇 연결 해제
            robot.logout()
        # 라이브러리 리소스 해제
        Auboi5Robot.uninitialize()

def move_rotate_test():
    # 로거 초기화
    logger_init()

    # 테스트 시작
    logger.info("{0} 테스트 시작 중...".format(Auboi5Robot.get_local_time()))

    # 시스템 초기화
    Auboi5Robot.initialize()

    # 로봇 제어 클래스 생성
    robot = Auboi5Robot()

    # 컨텍스트 생성
    handle = robot.create_context()

    # 컨텍스트 출력
    logger.info("robot.rshd={0}".format(handle))

    try:

        # 서버에 연결
        ip = '192.168.19.129'
        port = 8899
        result = robot.login(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("서버 {0}:{1}에 연결 실패.".format(ip, port))
        else:

            # 전원 재부팅
            # robot.robot_shutdown()

            # 전원 켜짐
            # robot.robot_startup()

            # 충돌 등급 설정
            # robot.set_collision_class(7)

            # joint_radian = (1, 0, 0, 0, 0, 0)
            # # 축을 초기 위치로 이동
            # robot.move_joint(joint_radian)

            joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
            logger.info("관절을 {0} 위치로 이동".format(joint_radian))
            robot.joint_move(joint_radian)

            # 현재 위치 가져오기
            current_pos = robot.get_current_waypoint()

            # 도구 회전 축 벡터(플랜지 기준, x=0, y=0, z축 0.1미터로 측정)
            tool_pos_on_end = (0, 0, 0.10)

            # 도구 자세(w,x,y,z 플랜지 기준, 알 수 없는 경우 기본값 사용)
            tool_ori_on_end = (1, 0, 0, 0)

            tool_desc = {"pos": tool_pos_on_end, "ori": tool_ori_on_end}

            # 플랜지 도구 끝점이 베이스 좌표계에서의 위치 얻기
            tool_pos_on_base = robot.base_to_base_additional_tool(current_pos['pos'],
                                                                current_pos['ori'],
                                                                tool_desc)

            logger.info("현재 위치={0}".format(current_pos['pos'][0]))

            logger.info("베이스의 도구 위치={0}".format(tool_pos_on_base['pos'][0]))

            # 도구 회전 축 벡터를 베이스 좌표계로 이동 (회전 방향은 오른손 법칙에 따름)
            rotate_axis = map(lambda a, b: a - b, tool_pos_on_base['pos'], current_pos['pos'])

            logger.info("회전 축={0}".format(rotate_axis))

            # 기본적으로 베이스 좌표계를 사용 (아래 값으로 기본 설정)
            user_coord = {'coord_type': RobotCoordType.Robot_Base_Coordinate,
                        'calibrate_method': 0,
                        'calibrate_points':
                            {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                            "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                            "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
                        'tool_desc':
                            {"pos": (0.0, 0.0, 0.0),
                            "ori": (1.0, 0.0, 0.0, 0.0)}
                        }

            # 회전 축 회전 함수 호출, 마지막 인자는 회전 각도(라디안)
            robot.move_rotate(user_coord, rotate_axis, 1)

            # 서버 연결 해제
            robot.logout()

    except RobotError as e:
        logger.error("로봇 이벤트:{0}".format(e))

    finally:
        # 서버 연결 해제
        if robot.connected:
            # 로봇 연결 해제
            robot.logout()
        # 라이브러리 리소스 해제
        Auboi5Robot.uninitialize()

def test_rsm():
    # 初始化logger
    logger_init()

    # 启动测试
    logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

    # 系统初始化
    Auboi5Robot.initialize()

    # 创建机械臂控制类
    robot = Auboi5Robot()

    # 创建上下文
    handle = robot.create_context()

    # 打印上下文
    logger.info("robot.rshd={0}".format(handle))

    try:

        # 链接服务器
        #ip = 'localhost'
        ip = '192.168.19.129'
        port = 8899
        result = robot.login(ip, port)
        
        #robot.enable_robot_event()

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("connect server{0}:{1} failed.".format(ip, port))
        else:

            # robot.move_pause()

            #joint_radian = (0, 0, 0, 0, 0, 0)
            # 轴动到初始位置
            #robot.move_joint(joint_radian)

            while True:
                time.sleep(0.05)

                rel = robot.set_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_02, 0)
                print(rel)
                print("++++++++++++++++++++++++")
                #result = robot.get_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_02)
                #print(result)
                # print("*********************************")

                time.sleep(2)
                # rel1 = robot.set_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_02, 0)
                # print(rel1)
                # print("++++++++++++++++++++++++")

            # 断开服务器链接
            robot.disconnect()

    except RobotError as e:
        logger.error("robot Event:{0}".format(e))


    finally:
        # 断开服务器链接
        if robot.connected:
            # 断开机械臂链接
            robot.logout()
        # 释放库资源
        Auboi5Robot.uninitialize()

class GetRobotWaypointProcess(Process):
    def __init__(self):
        Process.__init__(self)
        self.isRunWaypoint = False
        self._waypoints = None


    def startMoveList(self, waypoints):
        if self.isRunWaypoint == True:
            return False
        else:
            self._waypoints = waypoints

    def run(self):
        # 로거 초기화
        logger_init()

        # 테스트 시작
        logger.info("{0} 테스트 시작 중...".format(Auboi5Robot.get_local_time()))

        # 시스템 초기화
        Auboi5Robot.initialize()

        # 로봇 제어 클래스 생성
        robot = Auboi5Robot()

        # 컨텍스트 생성
        handle = robot.create_context()

        # 컨텍스트 출력
        logger.info("robot.rshd={0}".format(handle))

        try:
            # 서버에 연결
            #ip = 'localhost'
            ip = '192.168.19.129'
            port = 8899
            result = robot.login(ip, port)

            if result != RobotErrorType.RobotError_SUCC:
                logger.info("서버 {0}:{1}에 연결 실패.".format(ip, port))
            else:
                while True:
                    time.sleep(2)
                    waypoint = robot.get_current_waypoint()
                    print(waypoint)
                    print("----------------------------------------------")


                # 서버 연결 해제
                robot.disconnect()

        except RobotError as e:
            logger.error("로봇 이벤트:{0}".format(e))

        except KeyboardInterrupt:
            # 서버 연결 해제
            if robot.connected:
                # 로봇 연결 해제
                robot.disconnect()
            # 라이브러리 리소스 해제
            Auboi5Robot.uninitialize()
            print("웨이포인트 가져오기 종료-------------------------")

def runWaypoint(queue):
    while True:
        # while not queue.empty():
        print(queue.get(True))

def test_process_demo():
    # Logger 초기화
    logger_init()

    # 테스트 시작
    logger.info("{0} 테스트 시작...".format(Auboi5Robot.get_local_time()))

    # 시스템 초기화
    Auboi5Robot.initialize()

    # 로봇 컨트롤러 클래스 생성
    robot = Auboi5Robot()

    # 컨텍스트 생성
    handle = robot.create_context()

    # 컨텍스트 출력
    logger.info("robot.rshd={0}".format(handle))

    try:

        # time.sleep(0.2)
        # process_get_robot_current_status = GetRobotWaypointProcess()
        # process_get_robot_current_status.daemon = True
        # process_get_robot_current_status.start()
        # time.sleep(0.2)

        queue = Queue()

        p = Process(target=runWaypoint, args=(queue,))
        p.start()
        time.sleep(5)
        print("프로세스 시작됨.")

        # 서버 연결
        #ip = 'localhost'
        ip = '192.168.19.129'
        port = 8899
        result = robot.login(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("{0}:{1} 서버 연결 실패.".format(ip, port))
        else:
            robot.enable_robot_event()
            robot.init_profile()
            joint_maxvelc = (2.596177, 2.596177, 2.596177, 3.110177, 3.110177, 3.110177)
            joint_maxacc = (17.308779/2.5, 17.308779/2.5, 17.308779/2.5, 17.308779/2.5, 17.308779/2.5, 17.308779/2.5)
            robot.set_joint_maxacc(joint_maxacc)
            robot.set_joint_maxvelc(joint_maxvelc)
            robot.set_arrival_ahead_blend(0.05)
            while True:
                time.sleep(1)

                joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
                robot.move_joint(joint_radian, True)

                joint_radian = (55.5/180.0*pi, -20.5/180.0*pi, -72.5/180.0*pi, 38.5/180.0*pi, -90.5/180.0*pi, 55.5/180.0*pi)
                robot.move_joint(joint_radian, True)

                joint_radian = (0, 0, 0, 0, 0, 0)
                robot.move_joint(joint_radian, True)

                print("-----------------------------")

                queue.put(joint_radian)

                # time.sleep(5)

                # process_get_robot_current_status.test()

                # print("-----------------------------")

                # 서버 연결 해제
            robot.disconnect()

    except KeyboardInterrupt:
        robot.move_stop()

    except RobotError as e:
        logger.error("로봇 이벤트:{0}".format(e))

    finally:
        # 서버 연결 해제
        if robot.connected:
        # 로봇 연결 해제
           robot.disconnect()
        # 라이브러리 자원 해제
        Auboi5Robot.uninitialize()
        print("실행 종료-------------------------")


if __name__ == '__main__':  
    
    robot = AuboRobot('192.168.19.129')
    handle = robot.create_context()
    ip = robot.ip
    port = robot.port
    
    # robot login
    robot.login(ip,port)
    print('IP = {0} / PORT = {1} / The robot has been connected!'.format(robot.ip,robot.port))
    
    # robot power on
    robot.power_on()
    print('The robot has been powered.')
    
    # joint movement 1
    joint_pos = (0.6, 0.4, -0.948709, -0.397018, -1.570800, 0.541673)
    print('move joint to {0} '.format(joint_pos))
    robot.joint_move(joint_pos)
    
    # move robot to zero position
    joint_pos = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
    print('reset to zero {0} '.format(joint_pos))
    robot.joint_move(joint_pos)
    
    # joint movement 2
    joint_pos = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
    print('move joint to {0} '.format(joint_pos))
    robot.joint_move(joint_pos)
          
    # move robot to zero position
    joint_pos = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
    print('reset to zero {0} '.format(joint_pos))
    robot.joint_move(joint_pos)
    
    # disconnected robot
    robot.logout()
    print('The robot has been disconnected.')
    print('{0} Test has been completed.'.format(robot.get_local_time()))  



        

    
















