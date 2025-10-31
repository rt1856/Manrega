# utils.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')  # e.g. mysql+pymysql://user:pass@localhost:3306/mgnrega_db

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL NOT SET in environment")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine))
