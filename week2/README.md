# Action Item Extractor

## Overview

Action Item Extractor is a FastAPI + SQLite application that converts free-form notes into actionable checklist items.

It supports two extraction modes:

- **Rule-based extraction** using pattern and heuristic matching
- **LLM-powered extraction** using Ollama (`llama3.1:8b` by default)

A minimal frontend is included to:

- submit notes
- run extraction (`Extract` / `Extract LLM`)
- mark action items done
- list saved notes

## Requirements

### System

- Python `>=3.10,<4.0`
- SQLite (bundled with Python)
- [Ollama](https://ollama.com/) installed and running locally (required for LLM extraction)

### Python packages

Dependencies are defined in the repository `pyproject.toml`:

- Runtime: `fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `ollama`, `openai`, `sqlalchemy`
- Dev/Test: `pytest`, `httpx`, `black`, `ruff`, `pre-commit`

## Setup and Run

From this project directory (`week2`):

1. Create and activate a virtual environment (example with Conda):

```bash
conda create -n cs146s python=3.10 -y
conda activate cs146s
```

2. Install dependencies:

```bash
poetry install --no-interaction
```

3. (Optional) Configure LLM model:

```bash
set OLLAMA_ACTION_ITEMS_MODEL=llama3.1:8b
```

4. Start the app:

```bash
poetry run uvicorn app.main:app --reload
```

5. Open in browser:

- App UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Endpoints and Functionality

### Root / UI

- `GET /`
  - Serves the frontend (`frontend/index.html`)

### Notes

- `GET /notes`
  - Returns all notes (latest first)

- `POST /notes`
  - Creates a note
  - Request body:
    ```json
    { "content": "Meeting notes..." }
    ```

- `GET /notes/{note_id}`
  - Returns a single note by id
  - Returns `404` if not found

### Action items

- `POST /action-items/extract`
  - Extract action items from text
  - Supports optional rule-based or LLM path via `use_llm`
  - Request body:
    ```json
    { "text": "notes...", "save_note": true, "use_llm": false }
    ```

- `POST /action-items/extract-llm`
  - Dedicated LLM extraction endpoint
  - Request body:
    ```json
    { "text": "notes...", "save_note": true }
    ```

- `GET /action-items`
  - List all action items
  - Optional query param: `note_id`

- `POST /action-items/{action_item_id}/done`
  - Mark an action item done/undone
  - Request body:
    ```json
    { "done": true }
    ```
  - Returns `404` if action item is not found

## Running Tests

From this project directory:

```bash
poetry run pytest tests -v
```

If Poetry is unavailable but local venv exists:

```bash
../msec/Scripts/python.exe -m pytest tests -v
```

## Project Structure

```text
app/
  main.py
  db.py
  schemas.py
  routers/
    notes.py
    action_items.py
  services/
    extract.py
frontend/
  index.html
tests/
  test_extract.py
assignment.md
writeup.md
```
