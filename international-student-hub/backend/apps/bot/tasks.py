"""
bot/tasks.py — Celery tasks for the LINE Bot.

Using Celery here means the webhook endpoint returns 200 OK to LINE immediately,
while the actual HTTP call to LINE's API happens in the background.
LINE requires a response within 15 seconds — async processing ensures we never timeout.
"""

import logging
import requests

from django.conf import settings
from celery import shared_task

logger = logging.getLogger(__name__)

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_line_reply(self, reply_token: str, message_text: str):
    """
    Send a reply message to a LINE user.

    Args:
        reply_token: The replyToken from the LINE event (one-time use, expires in 30 days)
        message_text: The text to send back to the user

    Retries up to 3 times on network failure with a 5-second delay.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message_text,
            }
        ],
    }

    try:
        response = requests.post(LINE_REPLY_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"LINE reply sent successfully. Status: {response.status_code}")
    except requests.exceptions.RequestException as exc:
        logger.error(f"Failed to send LINE reply: {exc}")
        # Retry the task on failure
        raise self.retry(exc=exc)
