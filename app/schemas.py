# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    lead_id: str
    title: str
    status: str = "todo"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None

class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True
