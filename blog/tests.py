from datetime import datetime, timedelta, timezone

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Users

from .models import Posts


class PostViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = "/posts/"

        self.user = Users.objects.create_user(
            username="testuser", email="test@example.com", password="somepassword123"
        )
        self.other_user = Users.objects.create_user(
            username="otheruser", email="otheruser@test.com", password="password456"
        )

        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.other_user_token = str(
            RefreshToken.for_user(self.other_user).access_token
        )

        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.valid_payload = {"title": "First Post", "content": "My first post"}

        self.post1 = Posts.objects.create(
            title="Post 1",
            content="Content 1",
            username=self.user,
            author_ip="192.168.1.1",
            created_dateTime=datetime.now(timezone.utc) - timedelta(days=1),
            is_active=True,
        )

        self.post2 = Posts.objects.create(
            title="Post 2",
            content="Content 2",
            username=self.user,
            author_ip="192.168.1.1",
            created_dateTime=datetime.now(timezone.utc) - timedelta(days=1),
            is_active=True,
        )

    def test_list_posts_not_authenticated(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        self.assertNotIn("author_ip", response.data["results"][0])
        self.assertIn("author", response.data["results"][0])
        self.assertIn("created_at", response.data["results"][0])

    def test_list_posts_authenticated(self):
        response = self.client.get(self.base_url, **self.auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_posts_not_authenticated(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_posts_authenticated(self):
        response = self.client.post(
            self.base_url, self.valid_payload, format="json", **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("author_ip", response.data)
        self.assertIn("author", response.data)
        self.assertIn("created_at", response.data)

    def test_update_post_owner(self):
        edit_url = f"{self.base_url}{self.post1.id}/"
        data = {"title": "Updated Title", "content": "Updated Content"}

        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.patch(edit_url, data, format="json", **auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post_not_owner(self):
        edit_url = f"{self.base_url}{self.post1.id}/"
        data = {"title": "Updated Title 2", "content": "Updated Content 2"}

        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.other_user_token}"}
        response = self.client.patch(edit_url, data, format="json", **auth_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_owner(self):
        delete_url = f"{self.base_url}{self.post1.id}/"

        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(delete_url, **auth_headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.post1.refresh_from_db()
        self.assertFalse(self.post1.is_active)

    def test_delete_post_not_owner(self):
        delete_url = f"{self.base_url}{self.post1.id}/"
        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.other_user_token}"}
        response = self.client.delete(delete_url, **auth_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post1.refresh_from_db()
        self.assertTrue(self.post1.is_active)

    def test_delete_post_unauthenticated(self):
        delete_url = f"{self.base_url}{self.post1.id}/"
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.post1.refresh_from_db()
        self.assertTrue(self.post1.is_active)
