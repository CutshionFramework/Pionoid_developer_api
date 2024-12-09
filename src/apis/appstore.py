import subprocess
from flask import Blueprint, jsonify, request
import time
import requests
import os
import webbrowser

appstore = Blueprint('appstore', __name__)

# 미리 설정한 image_name과 container_name의 대응 딕셔너리
image_to_container_mapping = {
    "sromerof202/palletizing_app-server:latest": "palletizing_app_server",
    "another_image_name:latest": "another_container_name",
}

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
    installer_path = r"C:\temp\Docker Desktop Installer.exe"
    try:
        # 다운로드
        response = requests.get(installer_url, stream=True)
        with open(installer_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        # 설치 실행
        subprocess.run([installer_path, "--quiet", "--install"], check=True)
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

        # Docker 데몬 상태 확인
        if not is_docker_daemon_ready():
            return jsonify({"message": "Docker daemon is not ready. Please wait and try again."}), 500

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
                ["docker", "run", "-d", "--name", container_name, image_name],  # -d는 백그라운드 실행
                capture_output=True, text=True
            )

        if start_container_result.returncode == 0:
            webbrowser.open("http://localhost:5000")
            return jsonify({"message": "Docker Desktop opened and container started successfully"}), 200
        else:
            return jsonify({"message": "Failed to start container", "error": start_container_result.stderr}), 500

    except Exception as e:
        return jsonify({"message": "Error occurred while opening Docker Desktop and starting container", "error": str(e)}), 500


# @appstore.route('/api/get_app_state', methods=['GET'])
# def get_app_state():
#     try:
#         # Docker Desktop 설치 여부 확인
#         if not is_docker_installed():
#             return jsonify({"message": "Docker Desktop is not installed. Please install it first."}), 400

#         # Docker Desktop 실행 여부 확인
#         if not is_docker_daemon_ready():
#             docker_desktop_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
#             subprocess.Popen(docker_desktop_path, shell=True)
#             time.sleep(10)  # Docker 데몬이 실행될 시간을 기다림

#             if not is_docker_daemon_ready():
#                 return jsonify({"message": "Docker daemon is not ready. Please wait and try again."}), 500

#         # 다운로드된 Docker 이미지 목록 확인
#         result = subprocess.run(
#             ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
#             capture_output=True, text=True
#         )

#         if result.returncode != 0:
#             return jsonify({"message": "Failed to retrieve images", "error": result.stderr}), 500

#         # 이미지 정보 파싱
#         images = result.stdout.strip().split('\n') if result.stdout.strip() else []
#         return jsonify({"message": "Docker is ready", "images": images}), 200

#     except Exception as e:
#         return jsonify({"message": "Error occurred", "error": str(e)}), 500

