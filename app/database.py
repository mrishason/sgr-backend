from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ 1. Connection URL ya SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sgr.db"

# ✅ 2. Tengeneza engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# ✅ 3. Tengeneza SessionLocal
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ✅ 4. Tengeneza declarative base
Base = declarative_base()

# ✅ 5. Function ya kupewa DB session (hutumika kwa Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
