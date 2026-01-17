import os
import time
from datetime import datetime, timedelta
import threading
import logging

from api.db import SessionLocal, engine
from Joblib.models import Job, Base
from api.redis_client import move_job_to_processing_list
from Joblib.job import normal_job_function, bigger_job_function, definite_fail_job_function, anything_else

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Configuration
PENDING_LIST = os.getenv("REDIS_PENDING_LIST", "pending_jobs")
PROCESSING_LIST = os.getenv("REDIS_PROCESSING_LIST", "processing_jobs")
WORKER_LEASE_SECONDS = int(os.getenv("WORKER_LEASE_SECONDS", "60"))  # 60 Seconds
LEASE_EXTENSION_SECONDS = 30
LEASE_RENEW_THRESHOLD_SECONDS = 10  # Renew lease if it's about to expire in 10 seconds

JOB_TYPE_MAP = {
    "NORMAL": normal_job_function,
    "DELAY": bigger_job_function,
    "FAIL": definite_fail_job_function,
}

def run_job_in_thread(job_func, result_dict):
    """Executes the job function in a thread and captures the outcome."""
    try:
        result_dict['result'] = job_func()
        result_dict['exception'] = None
    except Exception as e:
        result_dict['result'] = None
        result_dict['exception'] = e

def worker_loop():
    logging.info("Worker started. Listening for jobs...")
    while True:
        job_id = None
        db = None
        try:
            # Atomically move a job from pending to processing list, blocking indefinitely.
            logging.info(f"Attempting to fetch job from {PENDING_LIST}...")
            job_id = move_job_to_processing_list(timeout=0)

            if job_id:
                logging.info(f"Fetched job_id: {job_id}. Processing job...")
                db = SessionLocal()
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.status = "RUNNING"
                    job.visibility_deadline = datetime.now() + timedelta(seconds=WORKER_LEASE_SECONDS)
                    db.commit()
                    db.refresh(job)
                    logging.info(f"Job {job_id} status updated to RUNNING with deadline {job.visibility_deadline}.")

                    job_function = JOB_TYPE_MAP.get(job.type, anything_else)
                    logging.info(f"Executing job {job_id} of type {job.type} with function {job_function.__name__}")

                    result_dict = {}
                    job_thread = threading.Thread(target=run_job_in_thread, args=(job_function, result_dict))
                    job_thread.start()

                    # Monitor the job thread and extend the lease if necessary.
                    while job_thread.is_alive():
                        # Wait for a short interval before checking again.
                        job_thread.join(timeout=5)
                        
                        if datetime.now() + timedelta(seconds=LEASE_RENEW_THRESHOLD_SECONDS) > job.visibility_deadline:
                            job.visibility_deadline += timedelta(seconds=LEASE_EXTENSION_SECONDS)
                            db.commit()
                            logging.info(f"Renewed lease for job {job_id}. New deadline: {job.visibility_deadline}")

                    # Job has finished, get the outcome.
                    exception = result_dict.get('exception')

                    if exception:
                        logging.error(f"Job {job_id} failed: {exception}")
                        job.status = "FAILED"
                    else:
                        logging.info(f"Job {job_id} completed successfully.")
                        job.status = "COMPLETED"
                    
                    db.commit()
                    logging.info(f"Job {job_id} status updated to {job.status}.")

                else:
                    logging.warning(f"Job {job_id} not found in database.")
        
        except Exception as e:
            if db:
                db.rollback()
            logging.error(f"An error occurred in worker loop for job {job_id}: {e}", exc_info=True)
            time.sleep(5)  # Wait before retrying.
        
        finally:
            if db:
                db.close()

if __name__ == "__main__":
    worker_loop()
