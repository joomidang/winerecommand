# src/database/setup.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 URL 설정 (환경 변수에서 읽기)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wine_recommendation.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# 와인 모델 정의
class Wine(Base):
    __tablename__ = "wines"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    country = Column(String)
    province = Column(String)
    region = Column(String)
    winery = Column(String)
    variety = Column(String)
    designation = Column(String)
    points = Column(Integer)
    price = Column(Float)
    description = Column(Text)
    taster_name = Column(String)
    taster_twitter_handle = Column(String)

def safe_string_value(value, default="Unknown"):
    """문자열 값을 안전하게 처리"""
    if pd.isna(value) or value is None or str(value).strip() == "":
        return default
    return str(value).strip()

def safe_float_value(value, default=None):
    """float 값을 안전하게 처리"""
    if pd.isna(value) or value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_value(value, default=0):
    """int 값을 안전하게 처리"""
    if pd.isna(value) or value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print("데이터베이스 테이블이 생성되었습니다.")

def analyze_na_values(df):
    """데이터프레임의 NA 값 분석"""
    print("\n=== NA 값 분석 ===")
    for column in df.columns:
        na_count = df[column].isna().sum()
        total_count = len(df)
        na_percentage = (na_count / total_count) * 100
        print(f"{column}: {na_count}/{total_count} ({na_percentage:.1f}%) NA 값")
    print("==================\n")

def get_available_datasets():
    """사용 가능한 데이터셋 목록 반환"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    datasets = []
    
    # 샘플 데이터셋 확인
    sample_csv = os.path.join(data_dir, "sample_wine_dataset.csv")
    
    if os.path.exists(sample_csv):
        datasets.append(("sample_csv", "샘플 데이터 (CSV)", sample_csv))
    
    # 실제 데이터셋 확인
    winemag_csv = os.path.join(data_dir, "winemag-data-130k-v2.csv")
    if os.path.exists(winemag_csv):
        datasets.append(("winemag", "실제 와인 데이터 (130K)", winemag_csv))
    
    return datasets

def load_data_from_file(file_path):
    """파일에서 데이터 로드"""
    try:
        df = pd.read_csv(file_path)
        
        print(f"CSV 파일에서 {len(df)}개의 데이터를 읽었습니다.")
        return df
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return None

def process_wine_data(df, dataset_type):
    """와인 데이터 처리 및 저장"""
    # NA 값 분석
    analyze_na_values(df)
    
    # 세션 생성
    db = SessionLocal()
    
    try:
        # 기존 데이터 삭제
        db.query(Wine).delete()
        
        # 데이터 처리 및 저장
        successful_inserts = 0
        failed_inserts = 0
        
        for index, row in df.iterrows():
            try:
                # 데이터셋 타입에 따라 컬럼 매핑
                if dataset_type == "winemag":
                    # 실제 데이터셋 컬럼 매핑
                    wine = Wine(
                        title=safe_string_value(row.get('title'), f'Unknown Wine {index + 1}'),
                        country=safe_string_value(row.get('country'), 'Unknown'),
                        province=safe_string_value(row.get('province'), 'Unknown'),
                        region=safe_string_value(row.get('region_1'), 'Unknown'),
                        winery=safe_string_value(row.get('winery'), 'Unknown'),
                        variety=safe_string_value(row.get('variety'), 'Unknown'),
                        designation=safe_string_value(row.get('designation'), 'Unknown'),
                        points=safe_int_value(row.get('points'), 0),
                        price=safe_float_value(row.get('price'), None),
                        description=safe_string_value(row.get('description'), 'No description available'),
                        taster_name=safe_string_value(row.get('taster_name'), 'Unknown'),
                        taster_twitter_handle=safe_string_value(row.get('taster_twitter_handle'), 'Unknown'),
                    )
                
                else:
                    # 샘플 데이터셋 컬럼 매핑 (기존 로직)
                    wine = Wine(
                        title=safe_string_value(row.get('title'), f'Unknown Wine {index + 1}'),
                        country=safe_string_value(row.get('country'), 'Unknown'),
                        province=safe_string_value(row.get('province'), 'Unknown'),
                        region=safe_string_value(row.get('region_1'), 'Unknown'),
                        winery=safe_string_value(row.get('winery'), 'Unknown'),
                        variety=safe_string_value(row.get('variety'), 'Unknown'),
                        designation=safe_string_value(row.get('designation'), 'Unknown'),
                        points=safe_int_value(row.get('points'), 0),
                        price=safe_float_value(row.get('price'), None),
                        description=safe_string_value(row.get('description'), 'No description available'),
                        taster_name=safe_string_value(row.get('taster_name'), 'Unknown'),
                        taster_twitter_handle=safe_string_value(row.get('taster_twitter_handle'), 'Unknown'),
                    )
                
                db.add(wine)
                successful_inserts += 1
                
            except Exception as e:
                print(f"행 {index + 1} 처리 중 오류: {e}")
                failed_inserts += 1
                continue
        
        db.commit()
        print(f"데이터베이스 저장 완료:")
        print(f"  - 성공: {successful_inserts}개")
        print(f"  - 실패: {failed_inserts}개")
        
        # 저장된 데이터 검증
        verify_data(db)
        
    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

def load_sample_data():
    """샘플 데이터 로드 (기존 함수 - 하위 호환성 유지)"""
    datasets = get_available_datasets()
    
    if not datasets:
        print("사용 가능한 데이터셋이 없습니다. 테스트용 샘플 데이터를 생성합니다.")
        create_test_data()
        return
    
    # 기본적으로 첫 번째 데이터셋 사용
    dataset_id, dataset_name, file_path = datasets[0]
    print(f"기본 데이터셋을 사용합니다: {dataset_name}")
    
    df = load_data_from_file(file_path)
    
    if df is not None:
        process_wine_data(df, dataset_id)
    else:
        print("데이터 로드에 실패했습니다. 테스트용 샘플 데이터를 생성합니다.")
        create_test_data()

def load_selected_data(dataset_choice=None):
    """선택된 데이터셋 로드"""
    datasets = get_available_datasets()
    
    if not datasets:
        print("사용 가능한 데이터셋이 없습니다. 테스트용 샘플 데이터를 생성합니다.")
        create_test_data()
        return
    
    # 사용자 선택 처리
    if dataset_choice is None:
        print("\n=== 사용 가능한 데이터셋 ===")
        for i, (dataset_id, dataset_name, file_path) in enumerate(datasets, 1):
            print(f"{i}. {dataset_name}")
        print("0. 테스트용 샘플 데이터 생성")
        
        try:
            choice = int(input("\n사용할 데이터셋을 선택하세요 (번호 입력): "))
            if choice == 0:
                create_test_data()
                return
            elif 1 <= choice <= len(datasets):
                dataset_id, dataset_name, file_path = datasets[choice - 1]
            else:
                print("잘못된 선택입니다. 첫 번째 데이터셋을 사용합니다.")
                dataset_id, dataset_name, file_path = datasets[0]
        except ValueError:
            print("숫자를 입력해주세요. 첫 번째 데이터셋을 사용합니다.")
            dataset_id, dataset_name, file_path = datasets[0]
    else:
        # 직접 선택된 데이터셋 사용
        for dataset_id, dataset_name, file_path in datasets:
            if dataset_id == dataset_choice:
                break
        else:
            print(f"선택된 데이터셋 '{dataset_choice}'을 찾을 수 없습니다. 첫 번째 데이터셋을 사용합니다.")
            dataset_id, dataset_name, file_path = datasets[0]
    
    print(f"\n선택된 데이터셋: {dataset_name}")
    
    df = load_data_from_file(file_path)
    
    if df is not None:
        process_wine_data(df, dataset_id)
    else:
        print("데이터 로드에 실패했습니다. 테스트용 샘플 데이터를 생성합니다.")
        create_test_data()

def create_test_data():
    """테스트용 샘플 데이터 생성"""
    db = SessionLocal()
    
    test_wines = [
        Wine(
            title="Test Cabernet Sauvignon 2020",
            country="France",
            province="Bordeaux",
            region="Medoc",
            winery="Chateau Test",
            variety="Cabernet Sauvignon",
            designation="Reserve",
            points=88,
            price=35.0,
            description="Rich and full-bodied wine with notes of blackcurrant and oak.",
            taster_name="Wine Expert",
            taster_twitter_handle="@wineexpert"
        ),
        Wine(
            title="Test Pinot Noir 2019",
            country="USA",
            province="California",
            region="Napa Valley",
            winery="Test Winery",
            variety="Pinot Noir",
            designation=None,  # NA 값 테스트
            points=92,
            price=None,  # NA 값 테스트
            description="Elegant wine with cherry and spice flavors.",
            taster_name=None,  # NA 값 테스트
            taster_twitter_handle=None  # NA 값 테스트
        ),
        Wine(
            title="Test Chardonnay 2021",
            country="Australia",
            province="Victoria",
            region="Yarra Valley",
            winery="Aussie Wines",
            variety="Chardonnay",
            designation="Single Vineyard",
            points=85,
            price=28.5,
            description="Crisp and refreshing with citrus and mineral notes.",
            taster_name="Aussie Taster",
            taster_twitter_handle="@aussietaster"
        )
    ]
    
    try:
        # 기존 데이터 삭제
        db.query(Wine).delete()
        
        # 테스트 데이터 추가
        for wine in test_wines:
            db.add(wine)
        
        db.commit()
        print(f"테스트용 {len(test_wines)}개의 와인 데이터가 생성되었습니다.")
        
        # 저장된 데이터 검증
        verify_data(db)
        
    except Exception as e:
        print(f"테스트 데이터 생성 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

def verify_data(db):
    """저장된 데이터 검증"""
    try:
        total_count = db.query(Wine).count()
        print(f"\n=== 저장된 데이터 검증 ===")
        print(f"총 와인 개수: {total_count}")
        
        # 샘플 데이터 출력
        sample_wines = db.query(Wine).limit(3).all()
        print("\n샘플 데이터:")
        for i, wine in enumerate(sample_wines, 1):
            print(f"{i}. {wine.title}")
            print(f"   국가: {wine.country}")
            print(f"   품종: {wine.variety}")
            print(f"   점수: {wine.points}")
            print(f"   가격: {wine.price if wine.price is not None else 'N/A'}")
            print(f"   설명: {wine.description[:50]}...")
            print()
        
        # NA 값 통계
        null_prices = db.query(Wine).filter(Wine.price.is_(None)).count()
        null_designations = db.query(Wine).filter(Wine.designation.is_(None)).count()
        null_tasters = db.query(Wine).filter(Wine.taster_name.is_(None)).count()
        
        print(f"NULL 값 통계:")
        print(f"  - 가격 NULL: {null_prices}개")
        print(f"  - 상품명 NULL: {null_designations}개")
        print(f"  - 테이스터 NULL: {null_tasters}개")
        print("==========================\n")
        
    except Exception as e:
        print(f"데이터 검증 중 오류: {e}")

def get_db():
    """데이터베이스 세션 반환"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_wine_statistics():
    """와인 데이터 통계 조회"""
    db = SessionLocal()
    try:
        total_wines = db.query(Wine).count()
        countries = db.query(Wine.country).distinct().count()
        varieties = db.query(Wine.variety).distinct().count()
        avg_points = db.query(Wine.points).filter(Wine.points > 0).all()
        avg_price = db.query(Wine.price).filter(Wine.price.is_not(None)).all()
        
        if avg_points:
            avg_points_value = sum([w.points for w in avg_points]) / len(avg_points)
        else:
            avg_points_value = 0
            
        if avg_price:
            avg_price_value = sum([w.price for w in avg_price]) / len(avg_price)
        else:
            avg_price_value = 0
        
        return {
            "total_wines": total_wines,
            "countries": countries,
            "varieties": varieties,
            "avg_points": round(avg_points_value, 1),
            "avg_price": round(avg_price_value, 2)
        }
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    print("와인 데이터베이스 설정을 시작합니다...")
    
    # 테이블 생성
    create_tables()
    
    # 사용 가능한 데이터셋 확인
    datasets = get_available_datasets()
    print(f"\n사용 가능한 데이터셋: {len(datasets)}개")
    for dataset_id, dataset_name, file_path in datasets:
        print(f"  - {dataset_name}")
    
    # 데이터셋 선택 방법 (우선순위):
    # 1. .env 파일의 DATASET_CHOICE
    # 2. 명령행 인자
    # 3. 대화형 선택
    dataset_choice = None
    
    # .env 파일에서 확인 (이미 load_dotenv()로 로드됨)
    if os.getenv("DATASET_CHOICE"):
        dataset_choice = os.getenv("DATASET_CHOICE")
        print(f"\n.env 파일에서 선택된 데이터셋: {dataset_choice}")
    
    # 명령행 인자 확인
    elif len(sys.argv) > 1:
        dataset_choice = sys.argv[1]
        print(f"\n명령행 인자에서 선택된 데이터셋: {dataset_choice}")
    
    # 와인 데이터 로드
    if dataset_choice:
        load_selected_data(dataset_choice)
    else:
        load_selected_data()  # 대화형 선택
    
    # 통계 출력
    stats = get_wine_statistics()
    print("=== 데이터베이스 통계 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    print("========================")
    
    print("\n데이터베이스 설정이 완료되었습니다!")
    print("\n사용법:")
    print("1. .env 파일 사용: DATASET_CHOICE=sample_csv 설정 후 실행")
    print("2. 명령행 인자 사용: python src/database/setup.py sample_csv")
    print("3. 대화형 선택: python src/database/setup.py")