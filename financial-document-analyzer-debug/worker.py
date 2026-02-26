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
    # Runner: prefer RQ worker if Redis available; otherwise poll DB for queued jobs.
    # On Windows, RQ worker may attempt to use `fork` which is unsupported.
    # Fall back to DB-polling on Windows to ensure the worker runs reliably.
    if os.name == "nt":
        print("Windows detected — RQ worker may be unsupported. Using DB polling fallback.")
    else:
        try:
            import redis
            from rq import Worker, Queue, Connection

            REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            conn = redis.from_url(REDIS_URL)
            with Connection(conn):
                q = Queue("analyze")
                w = Worker([q])
                w.work()
            # If we reach here, the RQ worker started and will run until stopped.
        except Exception as e:
            # If RQ/Redis initialization fails, log the exception and fall back to DB polling
            import traceback
            print("RQ worker initialization failed — falling back to DB polling worker")
            print(str(e))
            traceback.print_exc()
    # Fallback: simple DB polling loop to process queued jobs synchronously
    import time
    print("Starting DB-polling worker loop")
    while True:
        try:
            session = SessionLocal()
            rec = session.query(AnalysisResult).filter(AnalysisResult.status == 'queued').order_by(AnalysisResult.created_at).first()
            if rec:
                print(f"Processing queued job {rec.id}")
                process_analysis(rec.id, rec.query, rec.file_path, rec.filename)
            else:
                time.sleep(2)
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(2)
