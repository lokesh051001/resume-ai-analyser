from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import JobApplication

URL = "/api/applications/"
PASSWORD = "S3cure-pass-xyz"
User = get_user_model()


class ApplicationApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password=PASSWORD)
        self.client.force_authenticate(self.user)

    def make(self, **overrides):
        data = {"company": "Example Technologies", "role": "Python Backend Developer"}
        data.update(overrides)
        return self.client.post(URL, data, format="json")

    def test_create_defaults_to_saved(self):
        response = self.make()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["status"], "saved")

    def test_company_is_required(self):
        response = self.client.post(URL, {"role": "Developer"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    def test_invalid_status_rejected(self):
        self.assertEqual(self.make(status="aplied").status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_filters_by_status_and_search(self):
        self.make(status="applied")
        self.make(company="Other Co", role="Data Analyst", status="saved")
        self.assertEqual(len(self.client.get(URL, {"status": "applied"}).json()), 1)
        self.assertEqual(len(self.client.get(URL, {"search": "analyst"}).json()), 1)

    def test_update_and_delete(self):
        pk = self.make().json()["id"]
        patched = self.client.patch(f"{URL}{pk}/", {"status": "interview"}, format="json")
        self.assertEqual(patched.json()["status"], "interview")
        self.assertEqual(self.client.delete(f"{URL}{pk}/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(JobApplication.objects.count(), 0)

    def test_requires_login(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(URL).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_is_set_from_logged_in_user(self):
        pk = self.make().json()["id"]
        self.assertEqual(JobApplication.objects.get(pk=pk).owner, self.user)

    def test_client_cannot_choose_owner(self):
        bob = User.objects.create_user("bob", password=PASSWORD)
        pk = self.make(owner=bob.pk).json()["id"]
        self.assertEqual(JobApplication.objects.get(pk=pk).owner, self.user)

    def test_other_users_cannot_see_or_change_records(self):
        pk = self.make().json()["id"]
        bob = User.objects.create_user("bob", password=PASSWORD)
        self.client.force_authenticate(bob)
        self.assertEqual(self.client.get(URL).json(), [])
        self.assertEqual(self.client.get(f"{URL}{pk}/").status_code, status.HTTP_404_NOT_FOUND)
        patched = self.client.patch(f"{URL}{pk}/", {"status": "offer"}, format="json")
        self.assertEqual(patched.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(f"{URL}{pk}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(JobApplication.objects.get(pk=pk).status, "saved")