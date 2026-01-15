from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from Joblib.models import Base  # Import Base

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)  # Create tables
SessionLocal = sessionmaker(bind=engine)

