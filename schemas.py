from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class LabelSubmitRequest(BaseModel):
    pair_id:int
    annotater_id:str=Field(...,min_length=1,max_length=255)
    chosen: Literal["A","B","tie","skip"]

class PromptPairResponse(BaseModel):
    id:int
    prompt:str
    response_a:str
    response_b:str

    class Config:
        from_attribures=True

class LabelDetailResponse(BaseModel):
    id:int
    prompt:str
    response_a:str
    response_b:str
    category:str
    annotator_id:str
    chosen:Optional[str]=None
    created_at:datetime
    labeled_at:Optional[datetime]=None

    class Config:
        from_attributes=True
