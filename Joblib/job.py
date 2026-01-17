import time
import random

def normal_job_function():
    """
    - NORMAL
    Simulates a normal job that sleeps for 10 seconds and has a 30% chance of failing.
    """
    print("Normal Job: Starting...")
    time.sleep(10)
    if random.random() < 0.3:
        print("Normal Job: Failed!")
        raise Exception("Normal Job failed due to simulated error.")
    print("Normal Job: Completed successfully.")
    return "Normal Job completed"

def bigger_job_function():
    """
    - DELAY
    Simulates a bigger job that sleeps for 100 seconds and has a 15% chance of failing.
    """
    print("Bigger Job: Starting...")
    time.sleep(100)
    if random.random() < 0.15:
        print("Bigger Job: Failed!")
        raise Exception("Bigger Job failed due to simulated error.")
    print("Bigger Job: Completed successfully.")
    return "Bigger Job completed"

def definite_fail_job_function():
    """
    - FAIL
    Simulates a job that always fails.
    """
    print("Definite Fail Job: Starting...")
    print("Definite Fail Job: Failed!")
    raise Exception("Definite Fail Job failed as intended.")

def anything_else():
    """
    If the job type doesn't match any just sleep for 10s
    """
    print("Job type not listed. Sleeping for 10 seconds...")
    time.sleep(10)
    print("Done!")
    raise Exception("Job type not listed. ")
