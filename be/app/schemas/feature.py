from pydantic import BaseModel

class FeatureBase(BaseModel):
    code: str
    name: str
    service: str

class FeatureCreate(FeatureBase):
    pass

class FeatureUpdate(FeatureBase):
    pass

class FeatureOut(FeatureBase):
    id: int

    class Config:
        from_attributes = True
