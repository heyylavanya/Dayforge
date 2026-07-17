"""
DynamoDB storage — stores brief history.
"""
import json
import logging
from datetime import datetime, timezone
import boto3

logger = logging.getLogger()

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
TABLE_NAME = "DayForgeBriefs"


def store_brief(date: str, brief: str, sources: dict) -> None:
    """
    Store a generated brief in DynamoDB.
    """
    try:
        table = dynamodb.Table(TABLE_NAME)
        
        table.put_item(
            Item={
                "date": date,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "brief": brief,
                "sources": json.dumps(sources),
                "brief_length": len(brief),
            }
        )
        
        logger.info("Brief stored for date: %s", date)
        
    except Exception as e:
        logger.error("DynamoDB store failed: %s", str(e))
