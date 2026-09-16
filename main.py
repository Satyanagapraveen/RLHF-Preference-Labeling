from fastapi import FastAPI,Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from typing import Optional
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from database import get_db
from collections import defaultdict, Counter
import schemas
import models
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RLHF Labeling API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

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

@app.get("/api/analytics", response_model=schemas.AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    human_labels = db.query(models.Label).filter(models.Label.annotator_id != "system").all()
    
    total_labels = len(human_labels)
    
    distribution = {"A": 0, "B": 0, "tie": 0, "skip": 0}
    for label in human_labels:
        if label.chosen in distribution:
            distribution[label.chosen] += 1
            
    prompt_groups = defaultdict(list)
    for label in human_labels:
        prompt_groups[label.prompt].append(label.chosen)
        
    multi_label_pairs = 0
    agreeing_pairs = 0
    
    for choices in prompt_groups.values():
        if len(choices) > 1:
            multi_label_pairs += 1
            most_common_count = Counter(choices).most_common(1)[0][1]
            if most_common_count > len(choices) / 2:
                agreeing_pairs += 1
                
    agreement_rate = (agreeing_pairs / multi_label_pairs) if multi_label_pairs > 0 else 0.0
    
    return {
        "total_labels": total_labels,
        "label_distribution": distribution,
        "agreement_rate": round(agreement_rate, 2)
    }

@app.get("/api/export")
def export_labels(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Label).filter(
        models.Label.annotator_id != "system",
        models.Label.chosen.in_(["A", "B"])
    )
    
    if category:
        query = query.filter(models.Label.category == category)
        
    def generate_jsonl():
        for row in query.yield_per(100):
            if row.chosen == "A":
                chosen_text = row.response_a
                rejected_text = row.response_b
            else:
                chosen_text = row.response_b
                rejected_text = row.response_a
                
            export_dict = {
                "prompt": row.prompt,
                "chosen": chosen_text,
                "rejected": rejected_text
            }
            
            yield json.dumps(export_dict) + "\n"
            
    headers = {
        "Content-Disposition": 'attachment; filename="labels.jsonl"'
    }
    
    return StreamingResponse(generate_jsonl(), media_type="application/x-jsonlines", headers=headers)