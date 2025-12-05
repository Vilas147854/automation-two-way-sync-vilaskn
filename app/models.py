from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .database import Base

class Task(Base):
    __tablename__='tasks'
    id=Column(Integer, primary_key=True, index=True)
    lead_id=Column(String,index=True,nullable=False)
    title=Column(String,nullable=False)
    status=Column(String,default="todo")
    last_synced_at=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())