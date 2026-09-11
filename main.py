from fastapi import FastAPI,Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db

app=FastAPI(title="RLHF Labeling API")

@app.get("/health")

def health(db: Session=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return{"status":"healthy","database":"connected"}
    except Exception as e:
        return {"status":"unhe1althy", "database":str(e)}



    