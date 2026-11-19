import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
  raise ValueError("Database URL is not set in environment")

if DATABASE_URL.startswith("postgresql://"):
  DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create SQLAlchemy engine connected to Neon Postgres
engine = create_engine(
  DATABASE_URL,
  pool_pre_ping=True,
  pool_recycle=300
)

# SessionLocal for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI helper to get a DB session
def get_db():
  db = SessionLocal()
  try: 
    yield db
  finally:
    db.close()