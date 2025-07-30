from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from database.setup import get_db, Wine
from models.recommendation_model import recommendation_model

router = APIRouter(prefix="/wines", tags=["wines"])

# Pydantic 모델
class WineResponse(BaseModel):
    id: int
    title: str
    country: str
    province: str
    region: str
    winery: str
    variety: str
    designation: Optional[str]
    points: int
    price: Optional[float]
    description: str
    taster_name: Optional[str]
    taster_twitter_handle: Optional[str]

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    wine_id: int
    wine_title: str
    similarity_score: float

class WineRecommendationResponse(BaseModel):
    target_wine: WineResponse
    recommendations: List[RecommendationResponse]
    total_recommendations: int
    model_info: Dict[str, Any]

@router.get("/", response_model=List[WineResponse])
def get_all_wines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 와인 목록 조회"""
    wines = db.query(Wine).offset(skip).limit(limit).all()
    return wines

@router.get("/search/", response_model=List[WineResponse])
def search_wines(
    country: Optional[str] = None,
    variety: Optional[str] = None,
    winery: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_points: Optional[int] = None,
    max_points: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """와인 검색"""
    query = db.query(Wine)
    
    if country:
        query = query.filter(Wine.country.ilike(f"%{country}%"))
    if variety:
        query = query.filter(Wine.variety.ilike(f"%{variety}%"))
    if winery:
        query = query.filter(Wine.winery.ilike(f"%{winery}%"))
    if min_price is not None:
        query = query.filter(Wine.price >= min_price)
    if max_price is not None:
        query = query.filter(Wine.price <= max_price)
    if min_points is not None:
        query = query.filter(Wine.points >= min_points)
    if max_points is not None:
        query = query.filter(Wine.points <= max_points)
    
    wines = query.all()
    return wines

@router.get("/stats/")
def get_wine_stats(db: Session = Depends(get_db)):
    """와인 통계 정보"""
    from database.setup import get_wine_statistics
    return get_wine_statistics()

@router.get("/model/status/")
def get_model_status():
    """추천 모델 상태 확인"""
    return recommendation_model.get_model_info()

@router.get("/{wine_id}/recommendations/", response_model=WineRecommendationResponse)
def get_recommendations(wine_id: int, top_k: int = 10, include_scores: bool = True, db: Session = Depends(get_db)):
    """특정 와인에 대한 추천 와인 목록 (유사도 점수 포함)"""
    # 대상 와인 조회
    target_wine = db.query(Wine).filter(Wine.id == wine_id).first()
    if target_wine is None:
        raise HTTPException(status_code=404, detail="와인을 찾을 수 없습니다")
    
    # 추천 모델이 로드되어 있는지 확인
    if not recommendation_model.is_loaded:
        raise HTTPException(status_code=503, detail="추천 모델이 로드되지 않았습니다. 서버를 재시작해주세요.")
    
    # 추천 와인 ID와 점수 목록 가져오기
    if include_scores:
        recommendations_with_scores = recommendation_model.get_recommendations_with_scores(wine_id, top_k)
        recommended_wine_ids = [wine_id for wine_id, _ in recommendations_with_scores]
        similarity_scores = [score for _, score in recommendations_with_scores]
    else:
        recommended_wine_ids = recommendation_model.get_recommendations(wine_id, top_k)
        similarity_scores = [1.0] * len(recommended_wine_ids)  # 기본값
    
    # 추천된 와인들의 상세 정보 조회
    recommended_wines = db.query(Wine).filter(Wine.id.in_(recommended_wine_ids)).all()
    
    # 와인 ID를 키로 하는 딕셔너리 생성
    wine_dict = {wine.id: wine for wine in recommended_wines}
    score_dict = {wine_id: score for wine_id, score in zip(recommended_wine_ids, similarity_scores)}
    
    # 응답 데이터 구성
    recommendations = []
    for wine_id in recommended_wine_ids:
        if wine_id in wine_dict:
            recommendations.append(RecommendationResponse(
                wine_id=wine_id,
                wine_title=wine_dict[wine_id].title,
                similarity_score=score_dict[wine_id]
            ))
    
    return WineRecommendationResponse(
        target_wine=target_wine,
        recommendations=recommendations,
        total_recommendations=len(recommendations),
        model_info=recommendation_model.get_model_info()
    )

@router.get("/{wine_id}/recommendations/simple/")
def get_recommendations_simple(wine_id: int, top_k: int = 10, db: Session = Depends(get_db)):
    """특정 와인에 대한 추천 와인 목록 (간단한 버전)"""
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    if wine is None:
        raise HTTPException(status_code=404, detail="와인을 찾을 수 없습니다")
    
    # 추천 모델이 로드되어 있는지 확인
    if not recommendation_model.is_loaded:
        raise HTTPException(status_code=503, detail="추천 모델이 로드되지 않았습니다. 서버를 재시작해주세요.")
    
    # 추천 와인 ID 목록 가져오기
    recommended_wine_ids = recommendation_model.get_recommendations(wine_id, top_k)
    
    # 추천된 와인들의 상세 정보 조회
    recommended_wines = db.query(Wine).filter(Wine.id.in_(recommended_wine_ids)).all()
    
    return {
        "wine_id": wine_id,
        "wine_title": wine.title,
        "recommendations": recommended_wines,
        "total_recommendations": len(recommended_wines)
    }

@router.get("/{wine_id}", response_model=WineResponse)
def get_wine(wine_id: int, db: Session = Depends(get_db)):
    """특정 와인 조회"""
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    if wine is None:
        raise HTTPException(status_code=404, detail="와인을 찾을 수 없습니다")
    return wine