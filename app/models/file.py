from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..db import Base

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    remote_path = Column(String, nullable=False)
    url = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
