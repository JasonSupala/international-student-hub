import shutil
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


TEST_MEDIA_ROOT = Path(__file__).resolve().parent / "test_media"


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProfileUploadTests(APITestCase):
    def tearDown(self):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_profile_avatar_upload(self):
        user = User.objects.create_user(username="student", password="pass12345")
        self.client.force_authenticate(user)
        avatar = SimpleUploadedFile(
            "avatar.gif",
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )

        response = self.client.patch(
            "/api/v1/auth/profile/",
            {"avatar": avatar, "first_name": "Ada"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Ada")
        self.assertTrue(user.profile.avatar.name.startswith("avatars/"))
