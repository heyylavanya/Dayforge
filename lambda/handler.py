"""
DayForge — Lambda Handler
Main entry point for the morning brief agent.
Triggered by EventBridge Scheduler at 6 AM daily.
"""
import json
import os
import logging
from datetime import datetime, timezone

from sources.weather import fetch_weather
from sources.github import fetch_github_activity
from sources.news import fetch_news
from ai.bedrock import generate_brief
from delivery.email import send_email
from storage.dynamo import store_brief

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Main Lambda handler - orchestrates the morning brief generation.
    """
    logger.info("DayForge agent triggered at %s", datetime.now(timezone.utc).isoformat())
    
    config = {
        "city": os.environ.get("CITY", "New York"),
        "github_username": os.environ.get("GITHUB_USERNAME", ""),
        "github_token": os.environ.get("GITHUB_TOKEN", ""),
        "openweather_key": os.environ.get("OPENWEATHER_API_KEY", ""),
        "news_api_key": os.environ.get("NEWS_API_KEY", ""),
        "email_to": os.environ.get("EMAIL_TO", ""),
        "email_from": os.environ.get("EMAIL_FROM", ""),
    }
    
    missing = [k for k, v in config.items() if not v and k != "github_token"]
    if missing:
        logger.error("Missing configuration: %s", missing)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Missing config: {missing}"})
        }
    
    try:
        logger.info("Fetching data from sources...")
        
        weather_data = fetch_weather(config["city"], config["openweather_key"])
        logger.info("Weather data fetched for %s", config["city"])
        
        github_data = fetch_github_activity(
            config["github_username"], 
            config["github_token"]
        )
        logger.info("GitHub activity fetched for %s", config["github_username"])
        
        news_data = fetch_news(config["news_api_key"])
        logger.info("News headlines fetched")
        
        logger.info("Invoking Amazon Bedrock for brief generation...")
        
        brief = generate_brief(
            weather=weather_data,
            github=github_data,
            news=news_data,
            city=config["city"],
            username=config["github_username"]
        )
        logger.info("Brief generated successfully (%d characters)", len(brief))
        
        logger.info("Sending email to %s...", config["email_to"])
        
        today = datetime.now(timezone.utc).strftime("%A, %B %d")
        subject = f"☀️ DayForge Morning Brief — {today}"
        
        send_email(
            to_address=config["email_to"],
            from_address=config["email_from"],
            subject=subject,
            body=brief
        )
        logger.info("Email sent successfully")
        
        logger.info("Storing brief in DynamoDB...")
        
        store_brief(
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            brief=brief,
            sources={
                "weather": weather_data,
                "github": github_data,
                "news": news_data
            }
        )
        logger.info("Brief stored in DynamoDB")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Morning brief generated and delivered",
                "date": datetime.now(timezone.utc).isoformat(),
                "brief_length": len(brief)
            })
        }
        
    except Exception as e:
        logger.error("Agent failed: %s", str(e), exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
