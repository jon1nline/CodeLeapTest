from datetime import timedelta

import jwt
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from CodeLeapBlog import settings
from users.models import Users

from .models import Posts


class PostViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = "/posts/"

        # 1. Create user, login and save tokens on cookies.
        self.user = Users.objects.create_user(
            username="testuser", email="test@example.com", password="somepassword123"
        )
        self.other_user = Users.objects.create_user(
            username="otheruser", email="otheruser@test.com", password="password456"
        )
        payload = {
            "id": self.user.id,
            "username": self.user.username,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        self.client.cookies.load({"access_token": token})

        self.valid_payload = {"title": "First Post", "content": "My first post"}

        self.post1 = Posts.objects.create(
            title="Post 1",
            content="Content 1",
            username=self.user,
            author_ip="192.168.1.1",
            created_dateTime=timezone.now() - timedelta(days=1),
            is_active=True,
        )

        self.post2 = Posts.objects.create(
            title="Post 2",
            content="Content 2",
            username=self.user,
            author_ip="192.168.1.1",
            created_dateTime=timezone.now() - timedelta(days=1),
            is_active=True,
        )

    def test_list_posts_not_authenticated(self):
        self.client.cookies["access_token"] = None
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_posts_authenticated(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_posts_not_authenticated(self):
        self.client.cookies["access_token"] = ""
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_posts_authenticated(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_post_owner(self):
        edit_url = f"{self.base_url}{self.post1.id}/"
        data = {"title": "Updated Title", "content": "Updated Content"}
        response = self.client.patch(edit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post_not_owner(self):
        payload = {
            "id": self.other_user.id,
            "username": self.other_user.username,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        self.client.cookies["access_token"] = token
        edit_url = f"{self.base_url}{self.post1.id}/"
        data = {"title": "Updated Title 2", "content": "Updated Content 2"}
        response = self.client.patch(edit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_owner(self):
        self.client.force_authenticate(user=self.user)
        delete_url = f"{self.base_url}{self.post1.id}/"
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.post1.refresh_from_db()
        self.assertFalse(self.post1.is_active)

    def test_delete_post_not_owner(self):
        payload = {
            "id": self.other_user.id,
            "username": self.other_user.username,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        self.client.cookies["access_token"] = token
        delete_url = f"{self.base_url}{self.post1.id}/"
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post1.refresh_from_db()
        self.assertTrue(self.post1.is_active)

    def test_delete_post_unauthenticated(self):
        self.client.cookies["access_token"] = ""
        delete_url = f"{self.base_url}{self.post1.id}/"
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.post1.refresh_from_db()
        self.assertTrue(self.post1.is_active)
