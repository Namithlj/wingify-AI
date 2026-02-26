import os
import traceback
from db import SessionLocal, AnalysisResult
from core import run_crew


def process_analysis(job_id: str, query: str, file_path: str, filename: str):
    """Job function executed by the worker. Updates DB with result and deletes file."""
    session = SessionLocal()
    rec = session.query(AnalysisResult).filter(AnalysisResult.id == job_id).first()
    if not rec:
        # Create a new record if missing
        rec = AnalysisResult(id=job_id, query=query, filename=filename, file_path=file_path, status="running")
        session.add(rec)
        session.commit()

    try:
        rec.status = "running"
        session.add(rec)
        session.commit()

        result = run_crew(query, file_path=file_path)

        rec.result = str(result)
        rec.status = "finished"
        rec.finished_at = __import__("datetime").datetime.utcnow()
        session.add(rec)
        session.commit()

    except Exception as e:
        rec.status = "failed"
        rec.result = f"{str(e)}\n" + traceback.format_exc()
        session.add(rec)
        session.commit()

    finally:
        # Cleanup uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass


if __name__ == "__main__":
    # Simple runner to process jobs from RQ 'analyze' queue if Redis is available.
    import redis
    from rq import Worker, Queue, Connection

    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    conn = redis.from_url(REDIS_URL)
    with Connection(conn):
        q = Queue("analyze")
        w = Worker([q])
        w.work()
