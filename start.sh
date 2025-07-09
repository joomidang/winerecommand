#!/bin/bash

echo "=== 와인 추천 시스템 시작 ==="

# 데이터베이스 초기화
echo "1. 데이터베이스 초기화 중..."
python src/init_db.py

# 애플리케이션 시작
echo "2. 애플리케이션 시작 중..."
python src/app.py 