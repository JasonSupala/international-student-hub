from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Post, Reply


class CommunityVoteTests(APITestCase):
    def setUp(self):
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
