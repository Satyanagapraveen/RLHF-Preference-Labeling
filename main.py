from fastapi import FastAPI,Depends, HTTPException, Query, status
from sqlalchemy import text, func
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
        models.Label.annotator_id=="system",
        ~models.Label.prompt.in_(labeled_prompts)
    ).first()

    if not next_pair:
        raise HTTPException(status_code=404,detail="No Unlabeled Pairs available.")
    return next_pair

@app.post("/api/labels", status_code=status.HTTP_201_CREATED)
def submit_label(label_data:schemas.LabelSubmitRequest, db:Session=Depends(get_db)):
    original_pair=db.query(models.Label).filter(models.Label.id==label_data.pair_id).first()
    if not original_pair:
        raise HTTPException(status_code=404,detail="Pair not Found")
    new_label=models.Label(
        prompt=original_pair.prompt,
        response_a=original_pair.response_a,
        response_b=original_pair.response_b,
        category=original_pair.category,
        annotator_id=label_data.annotator_id,
        chosen=label_data.chosen,
        labeled_at=func.now()
    )
    
    db.add(new_label)
    db.commit()
    
    return {"message": "Label submitted successfully"}