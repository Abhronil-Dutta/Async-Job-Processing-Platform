from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    job_type = Column(String, index=True)
    payload = Column(String)
    status = Column(String, default="pending")
    visibility_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    attempts = Column(Integer, default=0)

    def __repr__(self):
        return f"<Job(id='{self.id}', job_type='{self.job_type}', status='{self.status}')>"
