from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from api.db import SessionLocal
from api.redis_client import add_job_to_pending_list

from pydantic import BaseModel
from sqlalchemy import text
import json 

app = FastAPI()

class JobCreate(BaseModel):
    job_type: str
    payload: dict
    max_attempts: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db_check")
def db_check():
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"db":"connected",
                "result": result
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to get database {e}")
    finally:
        db.close()

@app.post("/jobs")
def create_jon(job: JobCreate):
    db = SessionLocal()
    try:
        query = text("""
            INSERT INTO jobs(job_type, payload, max_attempts)
            VALUES (:job_type, :payload, :max_attemps)
            RETURNING id, status

        """)
        result = db.execute(query, {
            "job_type": job.job_type,
            "payload": json.dumps(job.payload),
            "max_attemps": job.max_attempts,
        },
        ).fetchone()
        db.commit()

        job_id = str(result.id)
        add_job_to_pending_list(job_id)

        return {
            "job_id": job_id,
            "status": result.status
        }
    finally:
        db.close()

