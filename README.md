# Financial Document Analyzer — Final (debugged)

This is a debugged, runnable version of the Financial Document Analyzer. The repository includes deterministic bug fixes, safer agent/task prompts, a lightweight synchronous fallback for environments without LLMs, and optional asynchronous processing using Redis + RQ. Results persist to a local SQLite database.

Highlights
 - Deterministic fixes to prevent runtime import errors and hallucination-prone prompts.
 - Optional background processing via Redis + RQ (fallback to synchronous/DB polling if Redis unavailable).
 - SQLite persistence (`results.db`) for job records and results.

Quick start (recommended)

1. Install Python dependencies:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

2. (Recommended) Start Redis via Docker Compose (provided):

```bash
docker compose up -d redis
```

3. Start the API server (from repo root):

```bash
python -m uvicorn main:app --app-dir financial-document-analyzer-debug --reload
```

4. (Recommended) Start the worker in another terminal so jobs are processed asynchronously:

```bash
python financial-document-analyzer-debug/worker.py
```

Files and behavior
- `main.py` — FastAPI server. POST `/analyze` accepts a PDF and optional `query`. It saves the upload to `data/`, creates a DB record, then tries to enqueue the job to Redis. If Redis/RQ isn't available, the request runs synchronously (or worker fallback will poll the DB).
- `worker.py` — Job processor. Prefers Redis/RQ; falls back to a DB-polling loop if Redis unavailable.
- `db.py` — SQLAlchemy models and `init_db()` to create `results.db`.
- `tools.py` — PDF reader tool with a safe fallback if `langchain` isn't installed.
- `agents.py`, `task.py` — Sanitized agents and tasks to reduce hallucinations.

Testing the API

Health check:

```bash
curl http://127.0.0.1:8000/
# -> {"message":"Financial Document Analyzer API is running"}
```

Upload and analyze (example):

```bash
curl -X POST "http://127.0.0.1:8000/analyze" -F "file=@data/sample.pdf" -F "query=Quick demo"
```

If Redis is running and the worker is active, `/analyze` returns `{ status: "queued", job_id: <id> }`. Otherwise, it returns `{ status: "finished", job_id: <id>, analysis: <result> }` after synchronous processing.

Retrieve a result:

```bash
curl http://127.0.0.1:8000/result/<job_id>
```

Notes and constraints
- This project intentionally does not require any third-party LLM API keys. The `llm` slot in agents is left unset; the repo includes small local stubs (used for offline testing) rather than integrating a live LLM.
- If you want full CrewAI behavior, install the real `crewai` package and any associated credentials, then replace the local stubs.

Docker
- `docker-compose.yml` includes a `redis` service to run Redis quickly. Optionally you can add an `app` service to containerize the FastAPI server and worker.

What I changed and why
- Fixed missing/unsafe imports and added guarded fallbacks for `dotenv` and `langchain`.
- Sanitized agent backstories and task instructions to produce structured outputs and avoid hallucinations.
- Added DB persistence and a worker with Redis support and a DB-poll fallback so the project runs even without external services.

Next steps (optional)
- Replace local `crewai` stubs with the official package for production LLM usage.
- Add unit tests for `tools.FinancialDocumentTool` and `worker.process_analysis`.

If you'd like, I will now push these final changes to the remote repository and create a clean release branch or tag.
