import subprocess
from flask import Blueprint, jsonify, request
import time
import os
import webbrowser

appstore = Blueprint('appstore', __name__)

# 미리 설정한 image_name과 container_name의 대응 딕셔너리
image_to_container_mapping = {
    "sromerof202/palletizing_app-server:latest": "palletizing_app_server",
    "another_image_name:latest": "another_container_name",
}

image_to_image_id_mapping = {
    "sromerof202/palletizing_app-server:latest": "palletizing-robot",
    "another_image_name:latest": "another_container_name",
}

# 앱 목록 정의
app_list = [
    {
        "id": 1,
        "image_id": "gom-cook",
        "name": "Gom Cook",
        "description": "A cooking robot that supports personalized customized cooking",
        "app_state": "Get"
    },
    {
        "id": 2,
        "image_id": "drawing-robot",
        "name": "Drawing Robot",
        "description": "A robot that draws pictures by recognizing photos taken with a camera",
        "app_state": "Get"
    },
    {
        "id": 3,
        "image_id": "palletizing-robot",
        "name": "Palletizing Robot",
        "description": "A robot for stacking books in a publishing factory",
        "app_state": "Get"
    },
    {
        "id": 4,
        "image_id": "welding-robot",
        "name": "Welding Robot",
        "description": "A robot that performs hazardous welding tasks in place of humans",
        "app_state": "Get"
    }
]

def get_default_download_path():
    if os.name == "nt":  # Windows
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    elif os.name == "posix":  # macOS/Linux
        return os.path.join(os.path.expanduser("~"), "Downloads")
    else:
        raise NotImplementedError(f"Unsupported OS: {os.name}")

# Docker Desktop 설치 여부 확인 함수
def is_docker_installed():
    docker_desktop_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
    return os.path.exists(docker_desktop_path)

# Docker 데몬 상태 확인 함수
def is_docker_daemon_ready():
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

# Docker Desktop 자동 설치 함수 (옵션)
def install_docker_desktop():
    installer_url = "https://desktop.docker.com/win/stable/Docker Desktop Installer.exe"  # Docker Desktop 설치 파일 URL
    installer_path = os.path.join(get_default_download_path(), "Docker Desktop Installer.exe")
    print(f"installer path: {installer_path}")

    docker_exe_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"  # 설치된 실행 파일 경로

    try:
        # 다운로드된 설치 파일이 이미 존재하는지 확인
        if not os.path.exists(installer_path):
            # 브라우저로 다운로드 페이지 열기
            print("Installer not found. Opening the Docker Desktop download page in your browser...")
            webbrowser.open(installer_url)

            # 다운로드된 인스톨러가 설치될 때까지 기다림
            while not os.path.exists(installer_path):
                print("Waiting for Docker Desktop installer to download...")
                time.sleep(10)  # 10초 대기
        else:
            print("Installer already exists. Skipping download.")

        # 다운로드된 설치 파일 실행
        subprocess.run([installer_path], check=True)

        # 설치 완료를 기다림 (Docker 실행 파일이 존재하는지 확인)
        while not os.path.exists(docker_exe_path):
            print("Waiting for Docker Desktop installation to complete...")
            time.sleep(10)  # 10초 대기

        print("Docker Desktop installation detected.")

        return True
    except Exception as e:
        print(f"Failed to download or install Docker Desktop: {e}")
        return False

# 1. Docker Pull API
@appstore.route('/api/download', methods=['POST'])
def download():
    try:
        # 클라이언트에서 받은 JSON 데이터에서 image_name 추출
        data = request.get_json()
        image_name = data.get('image_name')

        if not image_name:
            return jsonify({"message": "image_name is required"}), 400

        # Docker Desktop 설치 여부 확인
        if not is_docker_installed():
            # Docker Desktop 자동 설치 시도
            install_success = install_docker_desktop()
            if not install_success:
                return jsonify({"message": "Docker Desktop installation failed. Please install it manually."}), 500

            # 설치 후 재확인
            if not is_docker_installed():
                return jsonify({"message": "Docker Desktop is still not installed after the attempt."}), 500

        # Docker Desktop 실행 여부 확인
        if not is_docker_daemon_ready():
            docker_desktop_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
            subprocess.Popen(docker_desktop_path, shell=True)
            time.sleep(10)  # Docker 데몬이 실행될 시간을 기다림

            if not is_docker_daemon_ready():
                return jsonify({"message": "Docker daemon is not ready. Please wait and try again."}), 500

        result = subprocess.run(
            ["docker", "pull", image_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return jsonify({"message": "Download successful", "output": result.stdout}), 200
        else:
            print(f"Error pulling image: {result.stderr}")
            return jsonify({"message": "Download failed", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

@appstore.route('/api/open', methods=['POST'])
def open_docker():
    try:
        data = request.get_json()
        image_name = data.get('image_name')

        if not image_name:
            return jsonify({"message": "image_name is required"}), 400

        # 이미지에 대응되는 컨테이너 이름 찾기
        container_name = image_to_container_mapping.get(image_name)

        if not container_name:
            return jsonify({"message": f"No container mapping found for image: {image_name}"}), 400

        # Docker Desktop 실행 파일 경로
        docker_desktop_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"

        # Docker Desktop이 이미 실행 중인지 확인
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Docker Desktop.exe"], capture_output=True, text=True
        )
        if "Docker Desktop.exe" not in result.stdout:
            # Docker Desktop 실행
            subprocess.Popen(docker_desktop_path, shell=True)
            time.sleep(5)  # 잠시 대기
        else:
            print("Docker Desktop is already running.")

        # Docker 데몬 상태 확인 (최대 2분 대기)
        max_wait_time = 120  # 최대 대기 시간(초)
        interval = 5  # 상태 확인 간격(초)
        elapsed_time = 0

        while not is_docker_daemon_ready():
            if elapsed_time >= max_wait_time:
                return jsonify({"message": "Docker daemon did not become ready in time. Please try again later."}), 500
            print("Waiting for Docker daemon to become ready...")
            time.sleep(interval)
            elapsed_time += interval

        print("Docker daemon is ready.")

        # 기존 컨테이너가 있는지 확인
        check_container_result = subprocess.run(
            ["docker", "ps", "-a", "-q", "--filter", f"name={container_name}"],
            capture_output=True, text=True
        )

        if check_container_result.returncode == 0 and check_container_result.stdout.strip():
            # 기존 컨테이너가 있으면 시작
            start_container_result = subprocess.run(
                ["docker", "start", container_name],
                capture_output=True, text=True
            )
        else:
            # 컨테이너가 없으면 새로 실행
            start_container_result = subprocess.run(
                ["docker", "run", "-d", "--name", container_name, "-p", "5000:5000", image_name], 
                capture_output=True, text=True
            )


        if start_container_result.returncode == 0:
            webbrowser.open("http://localhost:5000")
            return jsonify({"message": "Docker Desktop opened and container started successfully"}), 200
        else:
            return jsonify({"message": "Failed to start container", "error": start_container_result.stderr}), 500

    except Exception as e:
        return jsonify({"message": "Error occurred while opening Docker Desktop and starting container", "error": str(e)}), 500


@appstore.route('/api/get_app_state', methods=['GET'])
def get_app_state():
    try:
        global app_list

        # Docker Desktop 설치 여부 확인
        if not is_docker_installed():
            return jsonify({"message": "Docker Desktop is not installed. Please install it first."}), 400

        # Docker Desktop 실행 여부 확인
        if not is_docker_daemon_ready():
            docker_desktop_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
            subprocess.Popen(docker_desktop_path, shell=True)
            time.sleep(10)  # Docker 데몬이 실행될 시간을 기다림

            if not is_docker_daemon_ready():
                return jsonify({"message": "Docker daemon is not ready. Please wait and try again."}), 500

        # 다운로드된 Docker 이미지 목록 확인
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return jsonify({"message": "Failed to retrieve images", "error": result.stderr}), 500

        # 현재 Docker 이미지 목록
        images = result.stdout.strip().split('\n') if result.stdout.strip() else []
        print("images : ", images)

       # Docker 이미지에 따라 상태 업데이트
        for app in app_list:
            # image_to_image_id_mapping을 사용하여 이미지 매핑 확인
            for image_name, image_id in image_to_image_id_mapping.items():
                if image_name in images and app["image_id"] == image_id:
                    app["app_state"] = "Run"
                    print(app_list)

        return jsonify({"message": "App state retrieved successfully", "apps": app_list}), 200

    except Exception as e:
        return jsonify({"message": "Error occurred", "error": str(e)}), 500


