#!/bin/bash

echo "============================================================"
echo "텔레그램 파일 업로더 실행"
echo "============================================================"
echo ""

# Python 3.11이 있는지 확인
if command -v python3.11 &> /dev/null; then
    echo "Python 3.11을 사용합니다..."
    python3.11 telegram_uploader.py
elif command -v python3 &> /dev/null; then
    echo "python3을 사용합니다..."
    python3 telegram_uploader.py
elif command -v python &> /dev/null; then
    echo "python을 사용합니다..."
    python telegram_uploader.py
else
    echo "오류: Python이 설치되어 있지 않습니다."
    echo "Python 3.11을 설치해주세요."
    read -p "아무 키나 눌러 종료..."
    exit 1
fi

echo ""
echo "프로그램이 종료되었습니다."
