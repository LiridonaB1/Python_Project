import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # ✅ ADD THIS

HN_URL = "https://news.ycombinator.com/"
UA = "tech-news-tracker/1.0"

def scrape_hackernews(limit: int = 30) -> list[dict]:
    resp = requests.get(HN_URL, headers={"User-Agent": UA}, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("tr.athing")

    results: list[dict] = []
    for row in rows[:limit]:
        external_id = (row.get("id") or "").strip()

        title_el = row.select_one("span.titleline > a")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)

        href = (title_el.get("href") or "").strip()
        url = urljoin(HN_URL, href)  # ✅ CHANGE THIS (absolute URL)

        sub = row.find_next_sibling("tr")
        score_el = sub.select_one("span.score") if sub else None
        points = int(score_el.get_text(strip=True).split()[0]) if score_el else 0

        comments = 0
        if sub:
            sublinks = sub.select("td.subtext a")
            if sublinks:
                last = sublinks[-1].get_text(strip=True)
                if "comment" in last:
                    try:
                        comments = int(last.split()[0])
                    except Exception:
                        comments = 0

        results.append(
            {
                "source": "hackernews",
                "external_id": external_id,
                "title": title,
                "url": url,
                "points": points,
                "comments": comments,
            }
        )

    time.sleep(0.2)
    return results
