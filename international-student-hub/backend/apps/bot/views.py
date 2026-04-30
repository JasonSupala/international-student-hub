"""
bot/views.py — LINE Bot webhook handler + BotFAQ admin API.
"""

import hashlib
import hmac
import json
import logging
import base64

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import BotFAQ
from .serializers import BotFAQSerializer
from .tasks import send_line_reply  # Celery async task

logger = logging.getLogger(__name__)

# Default reply when no FAQ keyword matches
FALLBACK_MESSAGE = (
    "Hi! 👋 I'm the ISH Taiwan Bot.\n\n"
    "I can help with: ARC, SIM card, bank account, housing, hospital, food, transport.\n\n"
    "Try asking about one of those topics, or visit our website for full info!"
)


def verify_line_signature(body: bytes, signature: str) -> bool:
    """
    Verify the X-Line-Signature header to confirm the request is from LINE.
    LINE signs the request body with your Channel Secret using HMAC-SHA256.
    https://developers.line.biz/en/docs/messaging-api/receiving-messages/#verifying-signatures
    """
    channel_secret = settings.LINE_CHANNEL_SECRET.encode("utf-8")
    hash_digest = hmac.new(channel_secret, body, hashlib.sha256).digest()
    computed_signature = base64.b64encode(hash_digest).decode("utf-8")
    return hmac.compare_digest(computed_signature, signature)


def find_faq_response(user_message: str) -> str | None:
    """
    Case-insensitive keyword search across all active BotFAQ entries.
    Returns the response text of the first matching entry, or None.
    """
    message_lower = user_message.lower()
    # Fetch all active FAQs once (small table, safe to load into memory)
    faqs = BotFAQ.objects.filter(active=True)
    for faq in faqs:
        if faq.trigger_keyword.lower() in message_lower:
            return faq.response_text
    return None


@csrf_exempt  # LINE sends POST requests; CSRF token not applicable for webhooks
@api_view(["POST"])
@permission_classes([AllowAny])
def line_webhook(request):
    """
    POST /api/v1/bot/webhook/

    Entry point for all LINE Messaging API events.
    1. Verify the X-Line-Signature header
    2. Parse the events array from the body
    3. For each 'message' event of type 'text', find a FAQ match
    4. Dispatch a Celery task to send the reply asynchronously
    """
    # --- Step 1: Signature verification ---
    signature = request.META.get("HTTP_X_LINE_SIGNATURE", "")
    if not signature:
        logger.warning("LINE webhook called without X-Line-Signature header")
        return Response({"error": "Missing signature"}, status=status.HTTP_400_BAD_REQUEST)

    raw_body = request.body
    if not verify_line_signature(raw_body, signature):
        logger.warning("LINE webhook signature verification failed")
        return Response({"error": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)

    # --- Step 2: Parse the event payload ---
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

    events = payload.get("events", [])

    # --- Step 3 & 4: Handle each event ---
    for event in events:
        # We only handle text messages; ignore follows, joins, etc.
        if event.get("type") != "message":
            continue
        if event.get("message", {}).get("type") != "text":
            continue

        reply_token = event.get("replyToken")
        user_message = event["message"]["text"]

        if not reply_token:
            continue  # Some events (e.g. webhook test) have no replyToken

        # Find the appropriate response
        response_text = find_faq_response(user_message) or FALLBACK_MESSAGE

        # Dispatch Celery task — don't block the webhook response
        send_line_reply.delay(reply_token, response_text)

    # LINE requires a 200 OK response quickly, even if processing continues async
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


class BotFAQViewSet(viewsets.ModelViewSet):
    """
    Admin-only CRUD for FAQ entries.
    GET    /api/v1/bot/faqs/        → list all FAQs
    POST   /api/v1/bot/faqs/        → create new FAQ
    PATCH  /api/v1/bot/faqs/<id>/   → update FAQ
    DELETE /api/v1/bot/faqs/<id>/   → delete FAQ

    In production, restrict this to staff users only.
    """
    queryset = BotFAQ.objects.all()
    serializer_class = BotFAQSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ["active", "category"]
    search_fields = ["trigger_keyword", "response_text"]
