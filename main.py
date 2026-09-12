from fastapi import FastAPI,Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db
import schemas
import models

app=FastAPI(title="RLHF Labeling API")

@app.get("/health")

def health_check(db: Session=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return{"status":"healthy","database":"connected"}
    except Exception as e:
        return {"status":"unhe1althy", "database":str(e)}

@app.get("/api/pairs/next", response_model=schemas.PromptPairResponse)
def get_next_pair(annotator_id:str=Query(...,min_length=1), db:Session=Depends(get_db)):
    labeled_prompts = db.query(models.Label.prompt).filter(
        models.Label.annotator_id==annotator_id,
        models.Label.chosen.isnot(None)
    ).subquery()

    next_pair=db.query(models.Label).filter(
        ~models.Label.prompt.in_(labeled_prompts)
    ).first()

    if not next_pair:
        raise HTTPException(status_code=404,detail="No Unlabeled Pairs available.")
    return next_pair

    