#!/usr/bin/env python3
"""
텔레그램 파일 업로더 GUI 애플리케이션
로컬 컴퓨터에서 파일을 선택하여 텔레그램 봇을 통해 채팅방으로 전송합니다.
"""

import sys
import subprocess


def check_python_version():
    """Python 3.11 버전인지 확인합니다."""
    required_version = (3, 11)
    current_version = sys.version_info[:2]

    print("=" * 60)
    print("Python 버전 확인")
    print("=" * 60)
    print(f"현재 Python 버전: {current_version[0]}.{current_version[1]}")
    print(f"필요한 Python 버전: {required_version[0]}.{required_version[1]}")

    if current_version != required_version:
        print("\n" + "!" * 60)
        print("⚠️  경고: Python 3.11이 필요합니다!")
        print("!" * 60)
        print(f"\n현재 사용 중인 버전: Python {current_version[0]}.{current_version[1]}")
        print(f"필요한 버전: Python 3.11")
        print("\nPython 3.11을 설치하고 다음 명령으로 실행해주세요:")
        print("  python3.11 telegram_uploader.py")
        print("\n또는 pyenv를 사용하는 경우:")
        print("  pyenv install 3.11")
        print("  pyenv local 3.11")
        print("=" * 60 + "\n")

        response = input("그래도 계속 실행하시겠습니까? (y/N): ").strip().lower()
        if response != 'y':
            print("프로그램을 종료합니다.")
            sys.exit(1)
        else:
            print("\n⚠️  호환성 문제가 발생할 수 있습니다.\n")
    else:
        print("✓ Python 버전이 올바릅니다!")
        print("=" * 60 + "\n")


def check_and_install_packages():
    """필요한 패키지를 확인하고 자동으로 설치합니다."""
    required_packages = {
        'requests': 'requests'
    }

    missing_packages = []

    print("=" * 60)
    print("텔레그램 파일 업로더 - 패키지 확인 중...")
    print("=" * 60)

    # 각 패키지 확인
    for package_name, install_name in required_packages.items():
        try:
            __import__(package_name)
            print(f"✓ {package_name}: 이미 설치되어 있습니다.")
        except ImportError:
            print(f"✗ {package_name}: 설치되지 않았습니다.")
            missing_packages.append(install_name)

    # 설치되지 않은 패키지가 있으면 설치
    if missing_packages:
        print("\n" + "=" * 60)
        print(f"누락된 패키지를 설치합니다: {', '.join(missing_packages)}")
        print("=" * 60 + "\n")

        for package in missing_packages:
            try:
                print(f">>> {package} 설치 중...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(f"✓ {package} 설치 완료!\n")
            except subprocess.CalledProcessError as e:
                print(f"✗ {package} 설치 실패: {e}")
                print("\n수동으로 설치해주세요:")
                print(f"  pip install {package}\n")
                sys.exit(1)

        print("=" * 60)
        print("모든 패키지 설치가 완료되었습니다!")
        print("=" * 60 + "\n")
    else:
        print("\n모든 필수 패키지가 설치되어 있습니다.")
        print("=" * 60 + "\n")


# 프로그램 시작 전 Python 버전 확인
check_python_version()

# 프로그램 시작 전 패키지 확인 및 설치
check_and_install_packages()

# 필수 패키지 임포트
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import json
import os
from pathlib import Path
import threading


class TelegramUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("텔레그램 파일 업로더")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 설정 파일 경로
        self.config_file = Path.home() / '.telegram_uploader_config.json'

        # 선택된 파일 경로
        self.selected_file = None

        # GUI 구성
        self.create_widgets()

        # 저장된 설정 불러오기
        self.load_config()

    def create_widgets(self):
        """GUI 위젯 생성"""

        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 제목
        title_label = ttk.Label(
            main_frame,
            text="📤 텔레그램 파일 업로더",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 봇 토큰 입력
        ttk.Label(main_frame, text="봇 토큰:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.token_entry = ttk.Entry(main_frame, width=50, show="*")
        self.token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # 채팅 ID 입력
        ttk.Label(main_frame, text="채팅방 ID:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.chat_id_entry = ttk.Entry(main_frame, width=50)
        self.chat_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # 구분선
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20
        )

        # 파일 선택 섹션
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(file_frame, text="선택된 파일:", font=("Arial", 10)).pack(
            anchor=tk.W, pady=(0, 5)
        )

        self.file_label = ttk.Label(
            file_frame,
            text="파일이 선택되지 않았습니다.",
            foreground="gray",
            font=("Arial", 9)
        )
        self.file_label.pack(anchor=tk.W, pady=(0, 10))

        # 파일 선택 버튼
        self.select_button = ttk.Button(
            file_frame,
            text="📁 파일 선택",
            command=self.select_file,
            width=20
        )
        self.select_button.pack(anchor=tk.W)

        # 진행 상태 바
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.grid(row=5, column=0, columnspan=2, pady=20)

        # 상태 메시지
        self.status_label = ttk.Label(
            main_frame,
            text="파일을 선택하고 업로드 버튼을 클릭하세요.",
            font=("Arial", 9),
            foreground="blue"
        )
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(0, 20))

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)

        # 업로드 버튼
        self.upload_button = ttk.Button(
            button_frame,
            text="⬆️ 업로드",
            command=self.upload_file,
            width=15
        )
        self.upload_button.pack(side=tk.LEFT, padx=5)

        # 설정 저장 버튼
        self.save_config_button = ttk.Button(
            button_frame,
            text="💾 설정 저장",
            command=self.save_config,
            width=15
        )
        self.save_config_button.pack(side=tk.LEFT, padx=5)

        # 종료 버튼
        self.exit_button = ttk.Button(
            button_frame,
            text="❌ 종료",
            command=self.root.quit,
            width=15
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)

    def select_file(self):
        """파일 선택 대화상자 표시"""
        filename = filedialog.askopenfilename(
            title="업로드할 파일 선택",
            filetypes=[
                ("모든 파일", "*.*"),
                ("이미지 파일", "*.png *.jpg *.jpeg *.gif"),
                ("문서 파일", "*.pdf *.doc *.docx *.txt"),
                ("압축 파일", "*.zip *.rar *.7z"),
            ]
        )

        if filename:
            self.selected_file = filename
            # 파일명만 표시 (경로 제외)
            file_name = os.path.basename(filename)
            file_size = os.path.getsize(filename)
            file_size_mb = file_size / (1024 * 1024)

            self.file_label.config(
                text=f"{file_name} ({file_size_mb:.2f} MB)",
                foreground="green"
            )
            self.status_label.config(
                text="파일이 선택되었습니다. 업로드 버튼을 클릭하세요.",
                foreground="green"
            )

    def upload_file(self):
        """텔레그램으로 파일 업로드"""
        # 입력 검증
        bot_token = self.token_entry.get().strip()
        chat_id = self.chat_id_entry.get().strip()

        if not bot_token:
            messagebox.showerror("오류", "봇 토큰을 입력해주세요.")
            return

        if not chat_id:
            messagebox.showerror("오류", "채팅방 ID를 입력해주세요.")
            return

        if not self.selected_file:
            messagebox.showerror("오류", "업로드할 파일을 선택해주세요.")
            return

        if not os.path.exists(self.selected_file):
            messagebox.showerror("오류", "선택한 파일이 존재하지 않습니다.")
            return

        # 파일 크기 체크 (50MB 제한)
        file_size = os.path.getsize(self.selected_file)
        if file_size > 50 * 1024 * 1024:
            messagebox.showwarning(
                "경고",
                "파일 크기가 50MB를 초과합니다.\n"
                "텔레그램 봇 API는 최대 50MB까지만 지원합니다."
            )
            return

        # 별도 스레드에서 업로드 실행
        upload_thread = threading.Thread(
            target=self._upload_file_thread,
            args=(bot_token, chat_id)
        )
        upload_thread.daemon = True
        upload_thread.start()

    def _upload_file_thread(self, bot_token, chat_id):
        """파일 업로드를 별도 스레드에서 실행"""
        try:
            # UI 업데이트
            self.root.after(0, self._start_upload_ui)

            # 텔레그램 API URL
            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

            # 파일 열기
            with open(self.selected_file, 'rb') as file:
                files = {'document': file}
                data = {'chat_id': chat_id}

                # 업로드 요청
                response = requests.post(url, files=files, data=data, timeout=300)

            # 응답 처리
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    self.root.after(0, self._upload_success)
                else:
                    error_msg = result.get('description', '알 수 없는 오류')
                    self.root.after(0, lambda: self._upload_error(error_msg))
            else:
                self.root.after(0, lambda: self._upload_error(
                    f"HTTP 오류: {response.status_code}"
                ))

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self._upload_error(
                "업로드 시간 초과. 파일이 너무 크거나 네트워크가 느립니다."
            ))
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self._upload_error(
                f"네트워크 오류: {str(e)}"
            ))
        except Exception as e:
            self.root.after(0, lambda: self._upload_error(
                f"오류 발생: {str(e)}"
            ))

    def _start_upload_ui(self):
        """업로드 시작 시 UI 업데이트"""
        self.upload_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_label.config(
            text="업로드 중... 잠시만 기다려주세요.",
            foreground="orange"
        )

    def _upload_success(self):
        """업로드 성공 시 UI 업데이트"""
        self.progress.stop()
        self.upload_button.config(state=tk.NORMAL)
        self.select_button.config(state=tk.NORMAL)
        self.status_label.config(
            text="✅ 파일이 성공적으로 업로드되었습니다!",
            foreground="green"
        )
        messagebox.showinfo("성공", "파일이 텔레그램으로 전송되었습니다!")

        # 파일 선택 초기화
        self.selected_file = None
        self.file_label.config(
            text="파일이 선택되지 않았습니다.",
            foreground="gray"
        )

    def _upload_error(self, error_msg):
        """업로드 실패 시 UI 업데이트"""
        self.progress.stop()
        self.upload_button.config(state=tk.NORMAL)
        self.select_button.config(state=tk.NORMAL)
        self.status_label.config(
            text=f"❌ 업로드 실패: {error_msg}",
            foreground="red"
        )
        messagebox.showerror("업로드 실패", error_msg)

    def save_config(self):
        """설정 저장"""
        bot_token = self.token_entry.get().strip()
        chat_id = self.chat_id_entry.get().strip()

        if not bot_token or not chat_id:
            messagebox.showwarning(
                "경고",
                "봇 토큰과 채팅방 ID를 모두 입력해주세요."
            )
            return

        config = {
            'bot_token': bot_token,
            'chat_id': chat_id
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            self.status_label.config(
                text="설정이 저장되었습니다.",
                foreground="green"
            )
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 실패: {str(e)}")

    def load_config(self):
        """저장된 설정 불러오기"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                self.token_entry.insert(0, config.get('bot_token', ''))
                self.chat_id_entry.insert(0, config.get('chat_id', ''))

                self.status_label.config(
                    text="저장된 설정을 불러왔습니다.",
                    foreground="blue"
                )
            except Exception as e:
                print(f"설정 불러오기 실패: {e}")


def main():
    """메인 함수"""
    root = tk.Tk()
    app = TelegramUploaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
