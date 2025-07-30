#!/usr/bin/env python3
"""
와인 추천 시스템 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.recommendation_model import WineRecommendationModel
import time

def test_recommendation_system():
    """추천 시스템을 테스트합니다."""
    print("=== 와인 추천 시스템 테스트 시작 ===")
    
    # 모델 인스턴스 생성
    model = WineRecommendationModel()
    
    # 모델 정보 출력
    print(f"모델 사용 가능: {model.is_model_available()}")
    print(f"모델 정보: {model.get_model_info()}")
    
    # 모델 로드
    print("\n모델 로드 중...")
    start_time = time.time()
    success = model.load_model()
    load_time = time.time() - start_time
    
    if not success:
        print("❌ 모델 로드 실패!")
        return
    
    print(f"✅ 모델 로드 완료 (소요시간: {load_time:.2f}초)")
    print(f"로드된 모델 정보: {model.get_model_info()}")
    
    # 테스트용 와인 ID (실제 데이터에서 존재하는 ID 사용)
    test_wine_ids = [92352, 92353, 92354]  # 첫 번째 와인 ID들
    
    for wine_id in test_wine_ids:
        print(f"\n--- 와인 ID {wine_id} 테스트 ---")
        
        # 기본 추천 테스트
        start_time = time.time()
        recommendations = model.get_recommendations(wine_id, top_k=5)
        rec_time = time.time() - start_time
        
        print(f"추천 결과 (상위 5개): {recommendations}")
        print(f"추천 생성 시간: {rec_time:.4f}초")
        
        # 점수 포함 추천 테스트
        start_time = time.time()
        recommendations_with_scores = model.get_recommendations_with_scores(wine_id, top_k=5)
        rec_time = time.time() - start_time
        
        print(f"추천 결과 (점수 포함):")
        for wine_id_rec, score in recommendations_with_scores:
            print(f"  와인 ID {wine_id_rec}: 유사도 {score:.4f}")
        print(f"추천 생성 시간: {rec_time:.4f}초")
        
        # 임베딩 벡터 가져오기 테스트
        embedding = model.get_wine_embedding(wine_id)
        if embedding is not None:
            print(f"임베딩 벡터 크기: {embedding.shape}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_recommendation_system() 