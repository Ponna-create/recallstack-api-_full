# 🧠 Recall Stack API

**AI Agent Memory Engine** — Log structured memories to reduce token waste and enable recall by action, reason, or outcome.

## 🚀 Features

- Log structured entries: `action`, `reason`, `outcome`
- Filter by `agent_id`, `session_id`, `context_id`, `tags`
- Sort and limit results
- Lightweight SQLite backend
- FastAPI with auto-generated docs (`/docs`)
- `/summary` endpoint for pattern detection
- `decay_score` and `created_at` fields for memory aging

## 🛠 Tech Stack

- FastAPI
- SQLite (MVP)
- Pydantic
- Uvicorn (ASGI server)

## 📦 Installation

```bash
git clone https://github.com/your-username/recallstack-api.git
cd recallstack-api
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📬 API Endpoints

### POST `/log`

```json
{
  "agent_id": "gpt-user123",
  "session_id": "session-2025-05-24",
  "context_id": "project-wklynuts",
  "action": "Launched landing page",
  "reason": "Test early demand",
  "outcome": "56 signups in 3 days",
  "tags": ["launch"],
  "decay_score": 0.9
}
```

### GET `/recall`
Filters: `agent_id`, `reason`, `context_id`, `tag`, `min_decay`, `limit`, `sort_by`

### GET `/recall/summary/{agent_id}`

Returns recent actions, top repeated reasons, high-value memories.

### PATCH `/log/{id}`  
Update `tags`, `outcome`, `decay_score`.

### DELETE `/log/{id}`  
Delete a memory log.

### GET `/health`  
Simple uptime check.

---

## 🌐 Deployment (Render)

- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 10000`
- Python Version: 3.11+

---

## 💡 Example Use Cases

- Agent memory for AutoGPT / LangChain
- AI decision trace logs
- Founder action journaling
- Knowledge assistant audit logs

---

## 📄 License

MIT – build, fork, and scale freely.
