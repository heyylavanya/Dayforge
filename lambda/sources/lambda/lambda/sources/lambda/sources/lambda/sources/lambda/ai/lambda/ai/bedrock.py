"""
Amazon Bedrock AI — Generates the morning brief using Nova Micro.
"""
import json
import logging
import boto3

logger = logging.getLogger()

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "amazon.nova-micro-v1:0"


def generate_brief(weather: dict, github: dict, news: dict, city: str, username: str) -> str:
    """
    Use Amazon Bedrock (Nova Micro) to generate a personalized morning brief.
    """
    context = f"""
You are DayForge, a personal AI morning brief assistant. Generate a concise, actionable morning brief.

DATA SOURCES:

WEATHER ({city}):
{json.dumps(weather, indent=2)}

GITHUB ACTIVITY ({username}):
{json.dumps(github, indent=2)}

NEWS HEADLINES:
{json.dumps(news, indent=2)}

INSTRUCTIONS:
- Write a warm, personalized morning brief
- Start with a greeting and weather summary
- Include practical advice (umbrella? sunscreen? jacket?)
- Summarize GitHub activity (PRs, issues, merges)
- List top 3 most relevant news headlines with brief context
- End with a "Today's Focus" suggestion based on the data
- Keep it concise — under 500 words
- Use emojis for section headers
- Be specific with numbers and details
- If any data source failed, gracefully skip that section
- Tone: friendly, professional, energizing
"""

    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": context}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 1024,
                    "temperature": 0.7,
                    "topP": 0.9,
                }
            })
        )
        
        result = json.loads(response["body"].read())
        
        output = result.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])
        
        if content and content[0].get("text"):
            return content[0]["text"]
        
        logger.error("Unexpected Bedrock response structure: %s", json.dumps(result)[:500])
        return _fallback_brief(weather, github, news, city)
        
    except Exception as e:
        logger.error("Bedrock invocation failed: %s", str(e))
        return _fallback_brief(weather, github, news, city)


def _fallback_brief(weather: dict, github: dict, news: dict, city: str) -> str:
    """Generate a basic brief without AI if Bedrock fails."""
    lines = [
        "☀️ DAYFORGE MORNING BRIEF",
        "=" * 30,
        "",
        f"🌤️ WEATHER — {city}",
    ]
    
    if weather.get("temperature"):
        lines.append(f"  {weather['temperature']}°F, {weather['description']}")
        lines.append(f"  High: {weather.get('high', 'N/A')}°F | Low: {weather.get('low', 'N/A')}°F")
    else:
        lines.append("  Weather data unavailable")
    
    lines.append("")
    lines.append("💻 GITHUB")
    
    if github.get("events_24h", 0) > 0:
        lines.append(f"  {github['events_24h']} events in last 24h")
        lines.append(f"  PRs: {github.get('pull_requests', 0)} | Issues: {github.get('issues', 0)}")
    else:
        lines.append("  No overnight activity")
    
    lines.append("")
    lines.append("📰 NEWS")
    
    for article in news.get("articles", [])[:3]:
        lines.append(f"  • {article['title']}")
    
    lines.append("")
    lines.append("Have a productive day! ☕")
    
    return "\n".join(lines)
