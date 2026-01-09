import os
from dotenv import load_dotenv
from fastapi import FastAPI
from database import engine, Base
from routers.articles import router as articles_router
from routers.api_key import router as auth_router

load_dotenv()  # loads .env

app = FastAPI(title="Tech News Tracker API")

# Create SQLite tables
Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api")
app.include_router(articles_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Tech News Tracker API running", "docs": "/docs"}
