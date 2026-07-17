"""
GitHub activity scanner — fetches overnight repo activity.
"""
import urllib.request
import json
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()


def fetch_github_activity(username: str, token: str) -> dict:
    """
    Fetch recent GitHub activity for a user.
    """
    if not username:
        return {"error": "No GitHub username configured", "events": []}
    
    try:
        url = f"https://api.github.com/users/{username}/received_events?per_page=30"
        
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "DayForge-Agent")
        if token:
            req.add_header("Authorization", f"token {token}")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            events = json.loads(response.read().decode())
        
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_events = []
        
        for event in events:
            event_time = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            if event_time < since:
                break
            recent_events.append({
                "type": event["type"],
                "repo": event["repo"]["name"],
                "time": event["created_at"],
                "actor": event.get("actor", {}).get("login", "unknown"),
            })
        
        repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
        req = urllib.request.Request(repos_url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "DayForge-Agent")
        if token:
            req.add_header("Authorization", f"token {token}")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            repos = json.loads(response.read().decode())
        
        pr_count = 0
        issue_count = 0
        for event in recent_events:
            if event["type"] == "PullRequestEvent":
                pr_count += 1
            elif event["type"] == "IssuesEvent":
                issue_count += 1
        
        return {
            "username": username,
            "events_24h": len(recent_events),
            "pull_requests": pr_count,
            "issues": issue_count,
            "active_repos": [r["name"] for r in repos[:5]],
            "recent_events": recent_events[:10],
        }
        
    except Exception as e:
        logger.warning("GitHub fetch failed: %s", str(e))
        return {
            "username": username,
            "error": str(e),
            "events_24h": 0,
            "recent_events": []
        }
