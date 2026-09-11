from fastapi import FastAPI

app=FastAPI(title="RLHF Labeling API")

@app.get("/health")

def health():
    return{"status":"healthy"}