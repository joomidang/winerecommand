import pickle
import os
from typing import List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class WineRecommendationModel:
    """와인 추천 모델 관리 클래스"""
    
    def __init__(self, model_path: str = "models/wine_recommendation_model.pkl", 
                 vectorizer_path: str = "models/wine_vectorizer.pkl"):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """모델과 벡터라이저를 로드합니다."""
        try:
            # 모델 파일 존재 확인
            if not os.path.exists(self.model_path):
                logger.warning(f"모델 파일을 찾을 수 없습니다: {self.model_path}")
                return False
                
            if not os.path.exists(self.vectorizer_path):
                logger.warning(f"벡터라이저 파일을 찾을 수 없습니다: {self.vectorizer_path}")
                return False
            
            # 모델과 벡터라이저 로드
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
                logger.info(f"모델 로드 완료: {self.model_path}")
                
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
                logger.info(f"벡터라이저 로드 완료: {self.vectorizer_path}")
                
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 중 오류 발생: {str(e)}")
            return False
    
    def get_recommendations(self, wine_id: int, top_k: int = 10) -> List[int]:
        """특정 와인 ID에 대한 추천 와인 ID 목록을 반환합니다."""
        if not self.is_loaded:
            logger.error("모델이 로드되지 않았습니다. 먼저 load_model()을 호출하세요.")
            return []
        
        try:
            # 여기서 실제 추천 로직을 구현합니다
            # 현재는 더미 데이터를 반환하지만, 실제로는 모델을 사용하여 추천을 생성합니다
            recommendations = self._generate_recommendations(wine_id, top_k)
            return recommendations
            
        except Exception as e:
            logger.error(f"추천 생성 중 오류 발생: {str(e)}")
            return []
    
    def _generate_recommendations(self, wine_id: int, top_k: int) -> List[int]:
        """실제 추천 로직을 구현합니다."""
        # TODO: 실제 모델을 사용한 추천 로직 구현
        # 현재는 더미 데이터를 반환합니다
        # 실제 구현에서는 다음과 같은 방식으로 동작할 것입니다:
        # 1. wine_id에 해당하는 와인 정보를 데이터베이스에서 가져옴
        # 2. 벡터라이저를 사용하여 와인 특성을 벡터화
        # 3. 모델을 사용하여 유사한 와인들을 찾음
        # 4. 상위 k개의 와인 ID를 반환
        
        # 임시로 더미 데이터 반환
        dummy_recommendations = [wine_id + i for i in range(1, top_k + 1)]
        return dummy_recommendations
    
    def is_model_available(self) -> bool:
        """모델 파일들이 사용 가능한지 확인합니다."""
        return (os.path.exists(self.model_path) and 
                os.path.exists(self.vectorizer_path))
    
    def get_model_info(self) -> dict:
        """모델 정보를 반환합니다."""
        return {
            "model_loaded": self.is_loaded,
            "model_path": self.model_path,
            "vectorizer_path": self.vectorizer_path,
            "model_available": self.is_model_available()
        }

# 전역 모델 인스턴스
recommendation_model = WineRecommendationModel() 