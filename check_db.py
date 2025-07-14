#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 데이터베이스 확인 스크립트
"""

import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def check_database():
    """데이터베이스 파일 존재 여부 확인"""
    # 환경변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL", "sqlite:///./wine_recommendation.db")
    
    # SQLite URL에서 파일 경로 추출
    if database_url.startswith("sqlite:///"):
        db_file = database_url.replace("sqlite:///", "")
        if db_file.startswith("./"):
            db_file = db_file[2:]  # "./" 제거
    else:
        db_file = "wine_recommendation.db"  # 기본값
    
    if not os.path.exists(db_file):
        print(f"❌ 데이터베이스 파일 '{db_file}'이 존재하지 않습니다.")
        print("먼저 데이터를 로드해야 합니다.")
        return False
    
    print(f"✅ 데이터베이스 파일 '{db_file}'을 찾았습니다.")
    return db_file

def show_table_info():
    """테이블 정보 표시"""
    try:
        # 데이터베이스 파일 경로 가져오기
        database_url = os.getenv("DATABASE_URL", "sqlite:///./wine_recommendation.db")
        
        # SQLite URL에서 파일 경로 추출
        if database_url.startswith("sqlite:///"):
            db_file = database_url.replace("sqlite:///", "")
            if db_file.startswith("./"):
                db_file = db_file[2:]  # "./" 제거
        else:
            db_file = "wine_recommendation.db"  # 기본값
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n📋 데이터베이스 테이블:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # wines 테이블이 있는 경우 상세 정보 표시
        if ('wines',) in tables:
            print("\n🍷 wines 테이블 정보:")
            
            # 컬럼 정보
            cursor.execute("PRAGMA table_info(wines);")
            columns = cursor.fetchall()
            print("  컬럼:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
            
            # 레코드 수
            cursor.execute("SELECT COUNT(*) FROM wines;")
            count = cursor.fetchone()[0]
            print(f"  총 레코드 수: {count:,}개")
            
            # 샘플 데이터 (처음 5개)
            if count > 0:
                print("\n  샘플 데이터 (처음 5개):")
                cursor.execute("SELECT * FROM wines LIMIT 5;")
                sample_data = cursor.fetchall()
                
                # 컬럼명 가져오기
                cursor.execute("PRAGMA table_info(wines);")
                column_names = [col[1] for col in cursor.fetchall()]
                
                # 데이터프레임으로 변환하여 보기 좋게 출력
                df = pd.DataFrame(sample_data, columns=column_names)
                print(df.to_string(index=False))
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 데이터베이스 확인 중 오류 발생: {e}")

def show_statistics():
    """와인 통계 정보 표시"""
    try:
        # 데이터베이스 파일 경로 가져오기
        database_url = os.getenv("DATABASE_URL", "sqlite:///./wine_recommendation.db")
        
        # SQLite URL에서 파일 경로 추출
        if database_url.startswith("sqlite:///"):
            db_file = database_url.replace("sqlite:///", "")
            if db_file.startswith("./"):
                db_file = db_file[2:]  # "./" 제거
        else:
            db_file = "wine_recommendation.db"  # 기본값
        
        conn = sqlite3.connect(db_file)
        
        print("\n📊 와인 통계:")
        
        # 국가별 와인 수
        df_country = pd.read_sql_query("""
            SELECT country, COUNT(*) as count 
            FROM wines 
            GROUP BY country 
            ORDER BY count DESC 
            LIMIT 10
        """, conn)
        print("\n🌍 국가별 와인 수 (상위 10개):")
        print(df_country.to_string(index=False))
        
        # 포인트 분포
        df_points = pd.read_sql_query("""
            SELECT 
                MIN(points) as min_points,
                MAX(points) as max_points,
                AVG(points) as avg_points,
                COUNT(*) as total_wines
            FROM wines
        """, conn)
        print("\n⭐ 포인트 통계:")
        print(df_points.to_string(index=False))
        
        # 가격 분포
        df_price = pd.read_sql_query("""
            SELECT 
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price) as avg_price,
                COUNT(*) as wines_with_price
            FROM wines 
            WHERE price IS NOT NULL
        """, conn)
        print("\n💰 가격 통계:")
        print(df_price.to_string(index=False))
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 통계 확인 중 오류 발생: {e}")

def main():
    """메인 함수"""
    print("🍷 와인 추천 시스템 - 데이터베이스 확인")
    print("=" * 50)
    
    db_file = check_database()
    if not db_file:
        return
    
    show_table_info()
    show_statistics()
    
    print("\n" + "=" * 50)
    print("✅ 데이터베이스 확인 완료!")

if __name__ == "__main__":
    main() 