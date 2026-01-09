from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import get_db
from models.article import Article, ArticleOut, ArticleListOut, ArticleSaveIn, RefreshOut
from auth.security import require_api_key
from scraper import scrape_hackernews

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListOut)
def list_articles(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="Search in title"),
    saved: bool | None = Query(default=None, description="Filter saved=true/false"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(Article)

    if q:
        stmt = stmt.where(Article.title.ilike(f"%{q}%"))
    if saved is not None:
        stmt = stmt.where(Article.saved == saved)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(
        stmt.order_by(Article.created_at.desc()).offset(offset).limit(limit)
    ).all()

    return {"items": items, "total": total}


@router.post("/refresh", response_model=RefreshOut)
def refresh_from_hn(
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    scraped = scrape_hackernews(limit=limit)

    inserted = 0
    updated = 0

    for a in scraped:
        existing = db.scalar(
            select(Article).where(
                Article.source == a["source"],
                Article.external_id == a["external_id"],
            )
        )

        if existing is None:
            db.add(
                Article(
                    source=a["source"],
                    external_id=a["external_id"],
                    title=a["title"],
                    url=a["url"],
                    points=a["points"],
                    comments=a["comments"],
                    saved=False,
                )
            )
            inserted += 1
        else:
            # update fields (but keep saved flag)
            existing.title = a["title"]
            existing.url = a["url"]
            existing.points = a["points"]
            existing.comments = a["comments"]
            existing.updated_at = datetime.utcnow()
            updated += 1

    db.commit()

    total_in_db = db.scalar(select(func.count()).select_from(Article))
    return {"inserted": inserted, "updated": updated, "total_in_db": total_in_db}


@router.patch("/{article_id}/save", response_model=ArticleOut)
def set_saved(
    article_id: int,
    payload: ArticleSaveIn,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.saved = payload.saved
    article.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    return article
