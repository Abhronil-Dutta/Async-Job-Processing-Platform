from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from api.db import SessionLocal
from api.redis_client import add_job_to_pending_list
from Joblib.models import Job

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
        return {"db": "connected", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to get database {e}")
    finally:
        db.close()

@app.post("/jobs", status_code=201)
def create_job(job_data: JobCreate):
    db = SessionLocal()
    try:
        new_job = Job(
            job_type=job_data.job_type,
            payload=job_data.payload,
            max_attempts=job_data.max_attempts
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        job_id = str(new_job.id)
        add_job_to_pending_list(job_id)

        return {
            "job_id": job_id,
            "status": new_job.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create job: {e}")
    finally:
        db.close()

