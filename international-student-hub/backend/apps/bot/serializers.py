"""
bot/serializers.py
"""

from rest_framework import serializers
from .models import BotFAQ


class BotFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotFAQ
        fields = [
            "id", "trigger_keyword", "response_text",
            "active", "category", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
