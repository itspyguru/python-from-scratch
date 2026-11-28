# pyGuru Banking AI: a banking app + a PydanticAI assistant

A small banking application (simulated money only) and an AI assistant that uses it safely.

- **Backend:** FastAPI, SQLite + SQLAlchemy 2.0, argon2 password hashing, JWT login, a ledger table,
  atomic transfers and idempotency keys.
- **Frontend:** a Streamlit dashboard (bank card, money in/out, balance chart, quick actions, history).
- **Assistant:** PydanticAI 2.77 with Gemini through OpenRouter. Tools call the FastAPI endpoints (never the
  database), transfers need your approval (deferred tools + an Approve / Reject card), hooks keep an audit log
  and block unapproved or too-large transfers, and an MCP server adds exchange rates, branches and an FAQ.

## Files

- `backend/`: `database.py`, `models.py`, `schemas.py`, `security.py`, `services/banking.py`, `routers/`, `main.py`
- `frontend/api.py`: the API client used by both the dashboard and the agent
- `frontend/app.py` + `style.css` + `.streamlit/config.toml`: the dashboard
- `frontend/agent.py`: the PydanticAI agent (tools, hooks, MCP, limits)
- `frontend/assistant.py`: the chat page with streaming and the approval card
- `frontend/test_agent.py`: try the approval flow from the terminal
- `mcp_server/bank_info.py`: the MCP server

## Run it

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # put your OpenRouter key in .env
uvicorn backend.main:app --reload            # terminal 1, API on http://127.0.0.1:8000/docs
cd frontend && streamlit run app.py          # terminal 2, app on http://localhost:8501
```

Register two users, add one as a beneficiary, then open **Assistant** and try "Send 500 to Rahul for lunch".
