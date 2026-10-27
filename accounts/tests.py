from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase

PASSWORD = "S3cure-pass-xyz"
User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        cache.clear()  # the login throttle counts requests in the cache

    def test_register_returns_token(self):
        r = self.client.post("/api/auth/register/", {"username": "alice", "password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertIn("token", r.json())
        self.assertNotIn(PASSWORD, r.content.decode())

    def test_weak_password_rejected(self):
        r = self.client.post("/api/auth/register/", {"username": "alice", "password": "12345678"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("password", r.json())

    def test_duplicate_username_rejected(self):
        User.objects.create_user("alice", password=PASSWORD)
        r = self.client.post("/api/auth/register/", {"username": "Alice", "password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("username", r.json())

    def test_login_then_logout_invalidates_token(self):
        User.objects.create_user("alice", password=PASSWORD)
        r = self.client.post("/api/auth/login/", {"username": "alice", "password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {r.json()['token']}")
        self.assertEqual(self.client.get("/api/applications/").status_code, 200)
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, 204)
        self.assertEqual(self.client.get("/api/applications/").status_code, 401)

    def test_bad_login_gives_same_message_for_unknown_user_and_wrong_password(self):
        User.objects.create_user("alice", password=PASSWORD)
        wrong = self.client.post("/api/auth/login/", {"username": "alice", "password": "nope"}, format="json")
        unknown = self.client.post("/api/auth/login/", {"username": "ghost", "password": "nope"}, format="json")
        self.assertEqual(wrong.status_code, 400)
        self.assertEqual(wrong.json(), unknown.json())