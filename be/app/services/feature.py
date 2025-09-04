from sqlalchemy.orm import Session
from app.model.feature import Feature
from app.schemas.feature import FeatureCreate, FeatureUpdate

def get_all_features(db: Session):
    return db.query(Feature).all()

def get_feature_by_id(db: Session, feature_id: int):
    return db.query(Feature).filter(Feature.id == feature_id).first()

def create_feature(db: Session, feature_in: FeatureCreate):
    new_feature = Feature(**feature_in.dict())
    db.add(new_feature)
    db.commit()
    db.refresh(new_feature)
    return new_feature

def update_feature(db: Session, feature_id: int, feature_in: FeatureUpdate):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        return None
    for key, value in feature_in.dict().items():
        setattr(feature, key, value)
    db.commit()
    return feature

def delete_feature(db: Session, feature_id: int):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if feature:
        db.delete(feature)
        db.commit()
    return feature
