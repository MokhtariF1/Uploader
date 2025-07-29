from pydantic import BaseModel
from datetime import datetime

class FileCreate(BaseModel):
    pass  # not used directly in request

class FileRead(BaseModel):
    id: int
    filename: str
    remote_path: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
