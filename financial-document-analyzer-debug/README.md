# Financial Document Analyzer - Debug Assignment

This repository contains a financial document analysis system built with CrewAI agents. I fixed deterministic bugs, improved prompt/task definitions, and added bonus features (Redis queue + SQLite persistence) while keeping the project lightweight and runnable.

## What I fixed

- agents.py
  - Replaced broken `llm = llm` initialization that caused an import error. Agents now have safe, concise role/goal/backstory text and `llm` is left unset by default.
- tools.py
  - Fixed undefined `Pdf` by importing a PDF loader or providing a minimal fallback when `langchain` is not available. Cleaned whitespace handling in the PDF reader.
- task.py
  - Rewrote task descriptions and expected outputs to avoid hallucination-prone instructions and to produce structured, useful outputs.
- main.py
  - Fixed file save/cleanup flow and added a robust API handler for `/analyze`.

## Bonus features implemented

- Queue worker: Redis + RQ support. If `REDIS_URL` is configured and Redis is running, the API enqueues jobs and `worker.py` processes them asynchronously.
- Database: SQLite persistence using SQLAlchemy; results are stored in `results.db` in table `analysis_results`.

These features are implemented in `worker.py`, `db.py`, and `main.py`.

## Setup (minimal)

1. Create a virtualenv and activate it.

```sh
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```sh
pip install -r requirements.txt
```

3. (Optional) Start Redis for asynchronous processing:

```sh
# Use Docker (recommended for portability)
docker run -p 6379:6379 redis:7
```

4. Start the API server:

```sh
python -m uvicorn main:app --app-dir financial-document-analyzer-debug --reload
```

5. (Optional) Start the worker in another terminal:

```sh
python financial-document-analyzer-debug/worker.py
```

## API

- GET /
  - Health check.
  - Response: {"message": "Financial Document Analyzer API is running"}

- POST /analyze
  - Multipart form-data: `file` (PDF upload), `query` (form string, optional)
  - Saves uploaded file to `data/`, creates a DB record and either enqueues a job (if Redis available) or runs synchronously.
  - Returns `{ status: 'queued', job_id: <id> }` when queued, or `{ status: 'finished', job_id: <id>, analysis: <result> }` when processed synchronously.

Example (curl):

```sh
curl -X POST "http://127.0.0.1:8000/analyze" -F "file=@data/sample.pdf" -F "query=Analyze this"
```

- GET /result/{job_id}
  - Returns DB record for the job id: status, result, filename, timestamps.

## Notes and constraints

- The code expects `crewai` to be installed for full agent/LLM behavior. I did not integrate any external LLM into the project; `llm` is intentionally left unset. This matches the assignment requirement to debug the repo (deterministic fixes + prompt improvements) without heavy integration.
- The queued worker and DB persistence are implemented to satisfy bonus requirements.

## Files changed (high level)

- `agents.py` — sanitized prompts and fixed LLM initialization
- `tools.py` — fixed PDF loader usage and text cleaning
- `task.py` — rewritten tasks and outputs
- `main.py` — API handler fixes, DB enqueue logic
- `db.py` — SQLAlchemy models and init
- `worker.py` — RQ-compatible worker job and CLI worker runner

## Next steps (optional)

- Replace `crewai` references with the real Crew.ai package and configure credentials when available.
- Add unit tests around `worker.process_analysis` and `tools.FinancialDocumentTool.read_data_tool`.

---

If you want, I can now:
- Run an end-to-end smoke test on your machine (I can start server+worker and POST `data/sample.pdf`).
- Prepare a clean ZIP / GitHub-ready commit with only the final files.

Which should I do next?