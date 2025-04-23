#!/bin/bash

# 현재 스크립트(MTE.sh)의 절대 경로 구하기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 해당 디렉토리로 이동해서 실행
cd "$SCRIPT_DIR"
python3 MTE.py

