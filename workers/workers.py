import os
import time
from datetime import datetime, timedelta

from api.db import SessionLocal, engine
from Joblib.models import Job, Base
import logging
from api.redis_client import move_job_to_processing_list


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Configuration
PENDING_LIST = os.getenv("REDIS_PENDING_LIST", "pending_jobs")
PROCESSING_LIST = os.getenv("REDIS_PROCESSING_LIST", "processing_jobs")
WORKER_LEASE_SECONDS = int(os.getenv("WORKER_LEASE_SECONDS", "60")) # 60 Seconds

def worker_loop():
    logging.info("Worker started. Listening for jobs...")
    while True:
        job_id = None
        try:
            # Atomically move a job from pending to processing list
            logging.info(f"Attempting to fetch job from {PENDING_LIST}...")
            job_id = move_job_to_processing_list(timeout=WORKER_LEASE_SECONDS)

            if job_id:
                logging.info(f"Fetched job_id: {job_id}. Updating status in DB...")
                db = SessionLocal()
                try:
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if job:
                        job.status = "RUNNING"
                        job.visibility_deadline = datetime.now() + timedelta(seconds=WORKER_LEASE_SECONDS)
                        db.commit()
                        db.refresh(job)
                        logging.info(f"Job {job_id} status updated to RUNNING with deadline {job.visibility_deadline}.")

                        # Here you would typically execute the job
                        logging.info(f"Simulating execution for job {job_id}...")
                        time.sleep(10) # Simulate work.. Later to be replaced by the different jobs in job.py

                        # For now, let's assume successful completion and move it out of processing
                        # In a real scenario, this would be more complex with success/failure handling
                        # and potentially moving to a 'completed' or 'failed' list.
                        # For this iteration, we'll just mark it as completed directly.
                        job.status = "COMPLETED"
                        db.commit()
                        logging.info(f"Job {job_id} marked as COMPLETED.")
                        # Remove from processing list (this is a simplified approach, a real system
                        # might have a separate mechanism for acknowledging completion and removing)
                        # For now, let's just let it stay in processing and rely on its status
                        # to indicate it's done.

                    else:
                        logging.warning(f"Job {job_id} not found in database. It might have been processed by another worker or removed.")
                        # If job not found, it might be a stale entry in Redis or already processed.
                        # We should ideally remove it from processing_list here, but brpoplpush doesn't
                        # return enough info to safely remove it without id. For now, rely on
                        # monitoring to clean up stale entries.
                except Exception as e:
                    db.rollback()
                    logging.error(f"Error updating job {job_id} in DB: {e}")
                finally:
                    db.close()
            else:
                logging.info("No jobs in pending_jobs. Waiting...")
        except Exception as e:
            logging.error(f"An unexpected error occurred in worker loop: {e}")
            if job_id:
                logging.warning(f"Job {job_id} was being processed when error occurred. It might be stuck in {PROCESSING_LIST}.")
            time.sleep(5) # Wait a bit before retrying after an error

if __name__ == "__main__":
    worker_loop()
