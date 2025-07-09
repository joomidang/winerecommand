#!/usr/bin/env python3
"""
와인 데이터베이스 초기화 스크립트
개발 편의를 위한 데이터셋 선택 기능 포함
"""

import os
import sys
from dotenv import load_dotenv
from database.setup import create_tables, get_available_datasets, load_selected_data, get_wine_statistics

# .env 파일 로드
load_dotenv()

def main():
    print("=== 와인 데이터베이스 초기화 ===")
    
    # 테이블 생성
    print("\n1. 데이터베이스 테이블 생성 중...")
    create_tables()
    
    # 사용 가능한 데이터셋 확인
    datasets = get_available_datasets()
    print(f"\n2. 사용 가능한 데이터셋: {len(datasets)}개")
    for i, (dataset_id, dataset_name, file_path) in enumerate(datasets, 1):
        print(f"   {i}. {dataset_name} ({dataset_id})")
    
    if not datasets:
        print("   사용 가능한 데이터셋이 없습니다.")
        return
    
    # 데이터셋 선택 (우선순위):
    # 1. .env 파일의 DATASET_CHOICE
    # 2. 명령행 인자
    # 3. 대화형 선택
    dataset_choice = None
    
    # .env 파일에서 확인
    if os.getenv("DATASET_CHOICE"):
        dataset_choice = os.getenv("DATASET_CHOICE")
        print(f"\n3. .env 파일에서 선택된 데이터셋: {dataset_choice}")
    
    # 명령행 인자 확인
    elif len(sys.argv) > 1:
        dataset_choice = sys.argv[1]
        print(f"\n3. 명령행 인자에서 선택된 데이터셋: {dataset_choice}")
    
    # 데이터 로드
    print("\n4. 데이터 로드 중...")
    if dataset_choice:
        load_selected_data(dataset_choice)
    else:
        load_selected_data()  # 대화형 선택
    
    # 통계 출력
    print("\n5. 데이터베이스 통계:")
    stats = get_wine_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n=== 초기화 완료 ===")
    print("\n사용법:")
    print("1. .env 파일 사용: DATASET_CHOICE=sample_csv 설정 후 실행")
    print("2. 명령행 인자 사용: python src/init_db.py sample_csv")
    print("3. 대화형 선택: python src/init_db.py")
    print("\n사용 가능한 데이터셋 ID:")
    for dataset_id, dataset_name, file_path in datasets:
        print(f"   - {dataset_id}: {dataset_name}")

if __name__ == "__main__":
    main() 