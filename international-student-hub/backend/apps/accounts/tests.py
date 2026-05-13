import shutil
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .serializers import MAX_AVATAR_STORED_SIZE, MAX_AVATAR_UPLOAD_SIZE


TEST_MEDIA_ROOT = Path(__file__).resolve().parent / "test_media"
TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "security-tests",
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
        "auth_login": "2/min",
        "auth_register": "2/hour",
        "auth_refresh": "100/min",
        "community_write": "2/min",
        "profile_update": "2/min",
        "webhook": "100/min",
    },
}


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProfileUploadTests(APITestCase):
    def tearDown(self):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_profile_avatar_upload(self):
        user = User.objects.create_user(username="student", password="pass12345")
        self.client.force_authenticate(user)
        avatar = self.image_upload("avatar.png", size=(64, 64))

        response = self.client.patch(
            "/api/v1/auth/profile/",
            {"avatar": avatar, "first_name": "Ada"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Ada")
        self.assertTrue(user.profile.avatar.name.startswith("avatars/"))

    def test_profile_avatar_rejects_upload_over_5mb(self):
        user = User.objects.create_user(username="student", password="pass12345")
        self.client.force_authenticate(user)
        avatar = SimpleUploadedFile(
            "avatar.png",
            b"x" * (MAX_AVATAR_UPLOAD_SIZE + 1),
            content_type="image/png",
        )

        response = self.client.patch(
            "/api/v1/auth/profile/",
            {"avatar": avatar},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)

    def test_profile_avatar_rejects_corrupt_image(self):
        user = User.objects.create_user(username="student", password="pass12345")
        self.client.force_authenticate(user)
        avatar = SimpleUploadedFile(
            "avatar.png",
            b"not really an image",
            content_type="image/png",
        )

        response = self.client.patch(
            "/api/v1/auth/profile/",
            {"avatar": avatar},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)

    def test_large_profile_avatar_is_resized_and_compressed(self):
        user = User.objects.create_user(username="student", password="pass12345")
        self.client.force_authenticate(user)
        avatar = self.image_upload("avatar.png", size=(1400, 900), color=(28, 120, 180))

        response = self.client.patch(
            "/api/v1/auth/profile/",
            {"avatar": avatar},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        avatar_path = Path(user.profile.avatar.path)
        self.assertLessEqual(avatar_path.stat().st_size, MAX_AVATAR_STORED_SIZE)
        with Image.open(avatar_path) as image:
            self.assertLessEqual(max(image.size), 512)

    def test_replacing_profile_avatar_deletes_old_file(self):
        user = User.objects.create_user(username="student", password="pass12345")
        self.client.force_authenticate(user)

        self.client.patch(
            "/api/v1/auth/profile/",
            {"avatar": self.image_upload("first.png", color=(255, 0, 0))},
            format="multipart",
        )
        user.refresh_from_db()
        old_path = Path(user.profile.avatar.path)
        self.assertTrue(old_path.exists())

        response = self.client.patch(
            "/api/v1/auth/profile/",
            {"avatar": self.image_upload("second.png", color=(0, 255, 0))},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(old_path.exists())
        user.refresh_from_db()
        self.assertTrue(Path(user.profile.avatar.path).exists())

    def test_media_url_can_serve_uploaded_file_when_enabled(self):
        self.assertEqual(settings.MEDIA_URL, "/media/")
        self.assertTrue(hasattr(settings, "SERVE_MEDIA_FILES"))

    def test_production_media_serving_defaults_disabled(self):
        from config.settings import prod

        self.assertFalse(prod.SERVE_MEDIA_FILES)

    @staticmethod
    def image_upload(name, size=(32, 32), color=(255, 255, 255)):
        buffer = BytesIO()
        Image.new("RGB", size, color=color).save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(
    CACHES=TEST_CACHES,
    REST_FRAMEWORK=TEST_REST_FRAMEWORK,
    JWT_REFRESH_COOKIE_SECURE=False,
)
class CookieAuthSecurityTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="student", password="pass12345")

    def test_login_sets_httponly_refresh_cookie_without_returning_refresh_token(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "student", "password": "pass12345"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")

    def test_refresh_uses_cookie_and_rotates_cookie_value(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "student", "password": "pass12345"},
            format="json",
        )
        old_cookie_value = login.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = old_cookie_value

        response = self.client.post("/api/v1/auth/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertIn(settings.JWT_REFRESH_COOKIE_NAME, response.cookies)
        self.assertNotEqual(
            old_cookie_value,
            response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value,
        )

    def test_refresh_rejects_missing_cookie(self):
        response = self.client.post("/api/v1/auth/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_clears_refresh_cookie(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "student", "password": "pass12345"},
            format="json",
        )
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = login.cookies[
            settings.JWT_REFRESH_COOKIE_NAME
        ].value
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post("/api/v1/auth/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value, "")

    def test_login_is_throttled(self):
        payload = {"username": "student", "password": "wrong"}

        self.client.post("/api/v1/auth/login/", payload, format="json")
        self.client.post("/api/v1/auth/login/", payload, format="json")
        response = self.client.post("/api/v1/auth/login/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_register_is_throttled(self):
        for index in range(2):
            self.client.post(
                "/api/v1/auth/register/",
                {
                    "username": f"new{index}",
                    "email": f"new{index}@example.com",
                    "password": "StrongPass123!",
                    "password2": "StrongPass123!",
                },
                format="json",
            )

        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "new3",
                "email": "new3@example.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
