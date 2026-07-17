"""
News headlines fetcher using NewsAPI.
"""
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger()


def fetch_news(api_key: str, topics: str = "technology,programming,AI") -> dict:
    """
    Fetch top headlines from NewsAPI.
    """
    if not api_key:
        return {"error": "No NewsAPI key configured", "articles": []}
    
    try:
        params = urllib.parse.urlencode({
            "apiKey": api_key,
            "language": "en",
            "pageSize": "10",
            "q": topics.split(",")[0],
        })
        url = f"https://newsapi.org/v2/top-headlines?{params}"
        
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "DayForge-Agent")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        articles = []
        for article in data.get("articles", [])[:5]:
            if article.get("title") and article["title"] != "[Removed]":
                articles.append({
                    "title": article["title"],
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "description": (article.get("description") or "")[:150],
                    "url": article.get("url", ""),
                })
        
        return {
            "topic": topics,
            "count": len(articles),
            "articles": articles,
        }
        
    except Exception as e:
        logger.warning("News fetch failed: %s", str(e))
        return {
            "error": str(e),
            "articles": []
        }
