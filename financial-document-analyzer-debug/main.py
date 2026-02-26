from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio

import redis
import rq
from db import init_db, AnalysisResult, SessionLocal
from core import run_crew
from agents import financial_analyst
from task import analyze_financial_document

app = FastAPI(title="Financial Document Analyzer")

# Initialize DB
init_db()

# Redis / RQ setup (used for job queue). Configure `REDIS_URL` in env to change.
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_conn = redis.from_url(REDIS_url := REDIS_URL)
    queue = rq.Queue("analyze", connection=redis_conn)
except Exception:
    # If Redis isn't available, fall back to None and process synchronously
    redis_conn = None
    queue = None

# `run_crew` is provided by `core.py` and imported above.

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations"""
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Save uploaded file (keep it for worker to process)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Validate query
    if not query:
        query = "Analyze this financial document for investment insights"

    # Create DB entry and return job id while the job runs
    session = SessionLocal()
    job_record = AnalysisResult(query=query.strip(), filename=file.filename, file_path=file_path, status="queued")
    session.add(job_record)
    session.commit()
    session.refresh(job_record)
    job_id = job_record.id

    # Enqueue job if Redis available, otherwise process synchronously
    if queue is not None:
        try:
            queue.enqueue("worker.process_analysis", job_id, query.strip(), file_path, file.filename)
            return {"status": "queued", "job_id": job_id}
        except Exception:
            # if enqueue fails (e.g., Redis not reachable), fall back to synchronous processing
            pass
    else:
        # Synchronous fallback
        try:
            result = run_crew(query.strip(), file_path=file_path)
            job_record.result = str(result)
            job_record.status = "finished"
            job_record.finished_at = __import__("datetime").datetime.utcnow()
            session.add(job_record)
            session.commit()
            return {"status": "finished", "job_id": job_id, "analysis": str(result)}
        except Exception as e:
            job_record.status = "failed"
            job_record.result = str(e)
            session.add(job_record)
            session.commit()
            raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")


@app.get('/result/{job_id}')
def get_result(job_id: str):
    session = SessionLocal()
    rec = session.query(AnalysisResult).filter(AnalysisResult.id == job_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": rec.id,
        "status": rec.status,
        "result": rec.result,
        "filename": rec.filename,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
        "finished_at": rec.finished_at.isoformat() if rec.finished_at else None,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)