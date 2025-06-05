
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3
import json
from datetime import datetime
import uuid
import os

app = FastAPI(
    title="Recall Stack API",
    description="AI Agent Memory Engine - Store and retrieve action-reason-outcome memories",
    version="1.0.0"
)

DB_PATH = "recall_stack.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_logs (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            context_id TEXT,
            action TEXT NOT NULL,
            reason TEXT NOT NULL,
            outcome TEXT,
            tags TEXT,
            decay_score REAL DEFAULT 1.0,
            timestamp TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_id ON memory_logs(agent_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON memory_logs(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_context_id ON memory_logs(context_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_logs(timestamp)')
    conn.commit()
    conn.close()

class MemoryLog(BaseModel):
    agent_id: str
    session_id: str
    context_id: Optional[str]
    action: str
    reason: str
    outcome: Optional[str]
    tags: Optional[List[str]] = []
    decay_score: Optional[float] = 0.8
    timestamp: Optional[str]

class MemoryResponse(MemoryLog):
    id: str
    created_at: str

class UpdateMemoryLog(BaseModel):
    tags: Optional[List[str]] = None
    decay_score: Optional[float] = None
    outcome: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/log", response_model=MemoryResponse)
async def create_memory_log(memory: MemoryLog):
    try:
        log_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        timestamp = memory.timestamp or created_at
        tags_json = json.dumps(memory.tags) if memory.tags else "[]"
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memory_logs 
            (id, agent_id, session_id, context_id, action, reason, outcome, tags, decay_score, timestamp, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_id, memory.agent_id, memory.session_id, memory.context_id,
            memory.action, memory.reason, memory.outcome, tags_json,
            memory.decay_score, timestamp, created_at
        ))
        conn.commit()
        conn.close()
        return MemoryResponse(id=log_id, **memory.dict(), timestamp=timestamp, created_at=created_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create memory log: {str(e)}")

@app.get("/recall", response_model=List[MemoryResponse])
async def recall_memories(
    agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context_id: Optional[str] = None,
    reason: Optional[str] = None,
    outcome: Optional[str] = None,
    action: Optional[str] = None,
    tag: Optional[str] = None,
    min_decay: Optional[float] = 0.0,
    limit: Optional[int] = 100,
    sort_by: Optional[str] = "timestamp"
):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = "SELECT * FROM memory_logs WHERE 1=1"
        params = []
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if context_id:
            query += " AND context_id = ?"
            params.append(context_id)
        if reason:
            query += " AND reason LIKE ?"
            params.append(f"%{reason}%")
        if outcome:
            query += " AND outcome LIKE ?"
            params.append(f"%{outcome}%")
        if action:
            query += " AND action LIKE ?"
            params.append(f"%{action}%")
        if tag:
            query += " AND tags LIKE ?"
            params.append(f'%"{tag}"%')
        if min_decay:
            query += " AND decay_score >= ?"
            params.append(min_decay)
        if sort_by in ["timestamp", "decay_score", "created_at"]:
            query += f" ORDER BY {sort_by} DESC"
        else:
            query += " ORDER BY timestamp DESC"
        query += " LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [MemoryResponse(
            id=row[0], agent_id=row[1], session_id=row[2], context_id=row[3],
            action=row[4], reason=row[5], outcome=row[6],
            tags=json.loads(row[7]), decay_score=row[8],
            timestamp=row[9], created_at=row[10]
        ) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recall memories: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
