import pickle
import os
import numpy as np
from typing import List, Optional, Tuple, Dict
import logging
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)

class WineRecommendationModel:
    """코사인 유사도 기반 와인 추천 모델 클래스"""
    
    def __init__(self, embeddings_path: str = None):
        # 기본 경로 설정 (Docker 환경과 로컬 환경 모두 고려)
        if embeddings_path is None:
            # 여러 가능한 경로를 시도
            possible_paths = [
                "src/models/converted_data.pkl",
                "models/converted_data.pkl", 
                "/app/src/models/converted_data.pkl",
                "/app/models/converted_data.pkl",
                "converted_data.pkl"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    embeddings_path = path
                    break
            else:
                # 어떤 경로도 존재하지 않으면 기본값 사용
                embeddings_path = "src/models/converted_data.pkl"
        
        self.embeddings_path = embeddings_path
        self.embeddings_dict = None
        self.wine_ids = None
        self.embeddings_matrix = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """임베딩 데이터를 로드하고 코사인 유사도 계산을 위한 행렬을 준비합니다."""
        # 이미 로드된 경우 성공 반환
        if self.is_loaded:
            logger.info("모델이 이미 로드되어 있습니다.")
            return True
            
        try:
            # 임베딩 파일 존재 확인
            if not os.path.exists(self.embeddings_path):
                logger.warning(f"임베딩 파일을 찾을 수 없습니다: {self.embeddings_path}")
                # 현재 작업 디렉토리와 가능한 경로들을 로그로 출력
                logger.info(f"현재 작업 디렉토리: {os.getcwd()}")
                logger.info(f"현재 디렉토리 내용: {os.listdir('.')}")
                if os.path.exists('src'):
                    logger.info(f"src 디렉토리 내용: {os.listdir('src')}")
                if os.path.exists('models'):
                    logger.info(f"models 디렉토리 내용: {os.listdir('models')}")
                return False
            
            # 임베딩 데이터 로드
            with open(self.embeddings_path, 'rb') as f:
                logger.info(f"임베딩 데이터 로드 시작: {self.embeddings_path}")
                self.embeddings_dict = pickle.load(f)
                logger.info(f"임베딩 데이터 로드 완료: {self.embeddings_path}")
                logger.info(f"총 와인 수: {len(self.embeddings_dict)}")
            
            # 와인 ID 리스트와 임베딩 행렬 준비
            self.wine_ids = list(self.embeddings_dict.keys())
            self.embeddings_matrix = np.array([self.embeddings_dict[wine_id] for wine_id in self.wine_ids])
            
            # 코사인 유사도 계산을 위해 정규화
            self.embeddings_matrix = normalize(self.embeddings_matrix, norm='l2')
            
            logger.info(f"임베딩 행렬 준비 완료: {self.embeddings_matrix.shape}")
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
            # 와인 ID가 존재하는지 확인
            if wine_id not in self.embeddings_dict:
                logger.warning(f"와인 ID {wine_id}가 데이터에 존재하지 않습니다.")
                return []
            
            # 해당 와인의 임베딩 벡터 가져오기
            target_embedding = self.embeddings_dict[wine_id].reshape(1, -1)
            target_embedding = normalize(target_embedding, norm='l2')
            
            # 모든 와인과의 코사인 유사도 계산
            similarities = cosine_similarity(target_embedding, self.embeddings_matrix)[0]
            
            # 유사도가 높은 순으로 정렬 (자기 자신 제외)
            similar_indices = np.argsort(similarities)[::-1][1:top_k+1]
            
            # 추천 와인 ID 목록 생성
            recommendations = [self.wine_ids[idx] for idx in similar_indices]
            
            logger.info(f"와인 ID {wine_id}에 대한 상위 {top_k}개 추천 생성 완료")
            return recommendations
            
        except Exception as e:
            logger.error(f"추천 생성 중 오류 발생: {str(e)}")
            return []
    
    def get_recommendations_with_scores(self, wine_id: int, top_k: int = 10) -> List[Tuple[int, float]]:
        """특정 와인 ID에 대한 추천 와인 ID와 유사도 점수를 함께 반환합니다."""
        if not self.is_loaded:
            logger.error("모델이 로드되지 않았습니다. 먼저 load_model()을 호출하세요.")
            return []
        
        try:
            # 와인 ID가 존재하는지 확인
            if wine_id not in self.embeddings_dict:
                logger.warning(f"와인 ID {wine_id}가 데이터에 존재하지 않습니다.")
                return []
            
            # 해당 와인의 임베딩 벡터 가져오기
            target_embedding = self.embeddings_dict[wine_id].reshape(1, -1)
            target_embedding = normalize(target_embedding, norm='l2')
            
            # 모든 와인과의 코사인 유사도 계산
            similarities = cosine_similarity(target_embedding, self.embeddings_matrix)[0]
            
            # 유사도가 높은 순으로 정렬 (자기 자신 제외)
            similar_indices = np.argsort(similarities)[::-1][1:top_k+1]
            
            # 추천 와인 ID와 유사도 점수 목록 생성
            recommendations = [(self.wine_ids[idx], similarities[idx]) for idx in similar_indices]
            
            logger.info(f"와인 ID {wine_id}에 대한 상위 {top_k}개 추천 (점수 포함) 생성 완료")
            return recommendations
            
        except Exception as e:
            logger.error(f"추천 생성 중 오류 발생: {str(e)}")
            return []
    
    
    def get_wine_embedding(self, wine_id: int) -> Optional[np.ndarray]:
        """특정 와인 ID의 임베딩 벡터를 반환합니다."""
        if not self.is_loaded:
            logger.error("모델이 로드되지 않았습니다. 먼저 load_model()을 호출하세요.")
            return None
        
        if wine_id not in self.embeddings_dict:
            logger.warning(f"와인 ID {wine_id}가 데이터에 존재하지 않습니다.")
            return None
        
        return self.embeddings_dict[wine_id]
    
    def is_model_available(self) -> bool:
        """임베딩 파일이 사용 가능한지 확인합니다."""
        return os.path.exists(self.embeddings_path)
    
    def get_model_info(self) -> dict:
        """모델 정보를 반환합니다."""
        info = {
            "model_loaded": self.is_loaded,
            "embeddings_path": self.embeddings_path,
            "model_available": self.is_model_available()
        }
        
        if self.is_loaded:
            info.update({
                "total_wines": len(self.embeddings_dict),
                "embedding_dimension": self.embeddings_matrix.shape[1] if self.embeddings_matrix is not None else None
            })
        
        return info

# 전역 모델 인스턴스
recommendation_model = WineRecommendationModel() 