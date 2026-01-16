import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
PENDING_LIST_NAME = os.getenv("REDIS_PENDING_LIST", "pending_jobs")
PROCESSING_LIST_NAME = os.getenv("REDIS_PROCESSING_LIST", "processing_jobs")

redis_client = None

def get_redis_client():
    """
    Returns a Redis client instance.
    """
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL)
    return redis_client

def add_job_to_pending_list(job_id: str):
    """
    Adds a job ID to the pending list.
    """
    r = get_redis_client()
    r.lpush(PENDING_LIST_NAME, job_id)

def move_job_to_processing_list(timeout: int = 0):
    """
    Atomically and blockingly moves a job from the pending list to the processing list.
    Returns the job ID or None if the timeout is reached.
    A timeout of 0 will block indefinitely.
    """
    r = get_redis_client()
    job_id = r.brpoplpush(PENDING_LIST_NAME, PROCESSING_LIST_NAME, timeout=timeout)
    if job_id:
        return job_id.decode('utf-8')
    return None
