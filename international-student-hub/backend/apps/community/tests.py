from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Post, Reply


TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "community-security-tests",
    }
}
TEST_REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/min",
        "user": "1000/min",
        "auth_login": "100/min",
        "auth_register": "100/hour",
        "auth_refresh": "100/min",
        "community_write": "2/min",
        "profile_update": "100/min",
        "webhook": "100/min",
    },
}


class CommunityVoteTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="student", password="pass12345")
        self.author = User.objects.create_user(username="author", password="pass12345")
        self.post = Post.objects.create(author=self.author, title="Bank account", body="How?")
        self.reply = Reply.objects.create(post=self.post, author=self.author, body="Bring ARC.")

    def test_post_upvote_toggles(self):
        self.client.force_authenticate(self.user)
        url = f"/api/v1/community/posts/{self.post.id}/upvote/"

        liked = self.client.post(url)
        self.assertEqual(liked.status_code, status.HTTP_200_OK)
        self.assertEqual(liked.data["upvotes"], 1)
        self.assertTrue(liked.data["has_upvoted"])

        unliked = self.client.post(url)
        self.assertEqual(unliked.status_code, status.HTTP_200_OK)
        self.assertEqual(unliked.data["upvotes"], 0)
        self.assertFalse(unliked.data["has_upvoted"])

    def test_reply_upvote_toggles(self):
        self.client.force_authenticate(self.user)
        url = f"/api/v1/community/replies/{self.reply.id}/upvote/"

        liked = self.client.post(url)
        self.assertEqual(liked.status_code, status.HTTP_200_OK)
        self.assertEqual(liked.data["upvotes"], 1)
        self.assertTrue(liked.data["has_upvoted"])

        unliked = self.client.post(url)
        self.assertEqual(unliked.status_code, status.HTTP_200_OK)
        self.assertEqual(unliked.data["upvotes"], 0)
        self.assertFalse(unliked.data["has_upvoted"])

    def test_upvote_count_does_not_go_below_zero(self):
        self.client.force_authenticate(self.user)
        self.post.upvoted_by.add(self.user)
        self.post.upvotes = 0
        self.post.save(update_fields=["upvotes"])

        response = self.client.post(f"/api/v1/community/posts/{self.post.id}/upvote/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["upvotes"], 0)
        self.assertFalse(response.data["has_upvoted"])

    def test_unauthenticated_upvote_is_blocked(self):
        response = self.client.post(f"/api/v1/community/posts/{self.post.id}/upvote/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(CACHES=TEST_CACHES, REST_FRAMEWORK=TEST_REST_FRAMEWORK)
class CommunityThrottleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pass12345")
        self.author = User.objects.create_user(username="author", password="pass12345")
        self.post = Post.objects.create(author=self.author, title="Bank account", body="How?")
        self.client.force_authenticate(self.user)

    def test_authenticated_community_writes_are_throttled(self):
        self.client.post(f"/api/v1/community/posts/{self.post.id}/upvote/")
        self.client.post(f"/api/v1/community/posts/{self.post.id}/upvote/")
        response = self.client.post(f"/api/v1/community/posts/{self.post.id}/upvote/")

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
