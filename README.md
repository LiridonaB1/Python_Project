# 📰 Tech News Tracker (Hacker News)

A full-stack mini project built with **FastAPI + Streamlit** that scrapes
Hacker News, stores articles in SQLite, and allows saving favorites.

## Features
- Scrape Hacker News articles
- Store data in SQLite
- Save / Unsave articles
- API key protected endpoints
- Streamlit UI dashboard

## Tech Stack
- FastAPI
- Streamlit
- SQLite
- SQLAlchemy
- BeautifulSoup

## How to run locally

1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/tech-news-tracker.git
cd tech-news-tracker
uvicorn main:app --port 8001 - for backend
streamlit run app.py - for frontend
