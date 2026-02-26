from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import uuid

Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text)
    filename = Column(String)
    file_path = Column(String)
    status = Column(String, default='queued')
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)


SQLITE_URL = 'sqlite:///results.db'
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
