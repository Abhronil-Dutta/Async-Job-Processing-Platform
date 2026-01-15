import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_redis_client():
    """
    Returns a Redis client instance.
    """
    return redis.from_url(REDIS_URL)

def brpoplpush_job(source_list: str, destination_list: str, timeout: int = 0):
    """
    Atomically pops a job from the source list and pushes it to the destination list.
    Blocks until a job is available or timeout is reached.
    """
    r = get_redis_client()
    job_id = r.brpoplpush(source_list, destination_list, timeout)
    return job_id.decode('utf-8') if job_id else None
