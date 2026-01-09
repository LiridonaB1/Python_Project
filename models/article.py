from datetime import datetime
from typing import List

from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy import String, Integer, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), default="hackernews", index=True)
    external_id: Mapped[str] = mapped_column(String(50), index=True)

    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(2000))

    points: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)

    saved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---------- Pydantic Schemas ----------

class ArticleOut(BaseModel):
    id: int
    source: str
    external_id: str
    title: str
    url: str
    points: int
    comments: int
    saved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleListOut(BaseModel):
    items: List[ArticleOut]
    total: int


class ArticleSaveIn(BaseModel):
    saved: bool = Field(..., description="Set article saved=true/false")


class RefreshOut(BaseModel):
    inserted: int
    updated: int
    total_in_db: int
