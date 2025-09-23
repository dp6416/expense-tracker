import os
from sqlalchemy import create_engine #create a dataase connection engine. engine to talk to the the database such as mysql, postgre etc
from sqlalchemy.orm import sessionmaker, declarative_base #makes database sessiom/ a session to query and make database #dec base:A function that gives you a base class for defining ORM models (tables in Python class form). 


#Database URL (SQLite for now)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
#connection
connect_args = {"check_same_thread":False} if DATABASE_URL.startswith("sqlite") else{}

#{"check_same_thread": False}
# This is a SQLite-specific setting.
# By default, SQLite connections are not thread-safe — it doesn’t allow using the same connection object across different threads.
# SQLAlchemy apps often run in multi-threaded environments (e.g., web servers).
# Setting check_same_thread=False tells SQLite:
# “It’s okay if multiple threads use the same connection.”
# ⚠️ But it’s safe only because SQLAlchemy manages sessions carefully. Without SQLAlchemy, using this flag recklessly could cause race conditions.
#engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)
## create database session - Each request gets a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

## Base class for models
Base = declarative_base()

#dependancy to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db #yield turn function into a generator. YIELD is used for memory purpose. 
    finally:
        db.close()



