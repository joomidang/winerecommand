from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database.setup import get_db, Wine

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

@router.get("/", response_model=List[WineResponse])
def get_all_wines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 와인 목록 조회"""
    wines = db.query(Wine).offset(skip).limit(limit).all()
    return wines

@router.get("/{wine_id}", response_model=WineResponse)
def get_wine(wine_id: int, db: Session = Depends(get_db)):
    """특정 와인 조회"""
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    if wine is None:
        raise HTTPException(status_code=404, detail="와인을 찾을 수 없습니다")
    return wine

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