from sqlalchemy import Column, Integer, String, DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    job_type = Column(String, nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    status = Column(String, nullable=False, default="PENDING", server_default="PENDING", index=True)
    attempts = Column(Integer, nullable=False, default=0, server_default='0')
    max_attempts = Column(Integer, nullable=False, default=5, server_default='5')
    visibility_deadline = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(String, nullable=True)
    result_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Job(id='{self.id}', job_type='{self.job_type}', status='{self.status}')>"
