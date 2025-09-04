from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import feature as service_feature  
from app.schemas.feature import FeatureCreate, FeatureUpdate, FeatureOut

router = APIRouter(prefix="/features", tags=["Features"])

@router.get("/", response_model=list[FeatureOut])
def list_features(db: Session = Depends(get_db)):
    return service_feature.get_all_features(db)

@router.get("/{feature_id}", response_model=FeatureOut)
def get_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = service_feature.get_feature_by_id(db, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@router.post("/", response_model=FeatureOut)
def create_feature(feature_in: FeatureCreate, db: Session = Depends(get_db)):
    return service_feature.create_feature(db, feature_in)

@router.put("/{feature_id}", response_model=FeatureOut)
def update_feature(feature_id: int, feature_in: FeatureUpdate, db: Session = Depends(get_db)):
    feature = service_feature.update_feature(db, feature_id, feature_in)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@router.delete("/{feature_id}")
def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    service_feature.delete_feature(db, feature_id)
    return {"detail": "Deleted"}
