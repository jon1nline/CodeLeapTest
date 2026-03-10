from datetime import datetime, timedelta, timezone

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Users
from utils.permissions import IsOwnerOrReadOnly

from .models import Posts
from .views import get_author_ip


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
        self.other_user_token = str(RefreshToken.for_user(self.other_user).access_token)

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

    def test_soft_deleted_post_not_in_list(self):
        self.post1.is_active = False
        self.post1.save()

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p["id"] for p in response.data["results"]]
        self.assertNotIn(self.post1.id, ids)
        self.assertIn(self.post2.id, ids)

    def test_create_post_missing_title(self):
        response = self.client.post(
            self.base_url,
            {"content": "no title here"},
            format="json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_post_missing_content(self):
        response = self.client.post(
            self.base_url,
            {"title": "No content"},
            format="json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_posts_ordering_newest_first(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        newer = self.client.post(
            self.base_url,
            {"title": "Newer Post", "content": "fresh"},
            format="json",
            **self.auth_headers,
        )
        self.assertEqual(newer.status_code, status.HTTP_201_CREATED)
        newer_id = newer.data["id"]

        response = self.client.get(self.base_url)
        self.assertEqual(response.data["results"][0]["id"], newer_id)

    def test_search_filter(self):
        response = self.client.get(self.base_url, {"search": "Post 1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in response.data["results"]]
        self.assertIn("Post 1", titles)
        self.assertNotIn("Post 2", titles)

    def test_nonexistent_post_returns_404(self):
        response = self.client.get(f"{self.base_url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_filter(self):
        response = self.client.get(self.base_url, {"query": "Content 1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in response.data["results"]]
        self.assertIn("Post 1", titles)
        self.assertNotIn("Post 2", titles)

    def test_author_filter(self):
        response = self.client.get(self.base_url, {"author": "testuser"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 2)

        response = self.client.get(self.base_url, {"author": "missing-user"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_get_author_ip_prefers_forwarded_header(self):
        request = self.client.get(
            self.base_url,
            HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.1",
            REMOTE_ADDR="127.0.0.1",
        ).wsgi_request

        self.assertEqual(get_author_ip(request), "203.0.113.10")

    def test_get_author_ip_falls_back_to_remote_addr(self):
        request = self.client.get(self.base_url, REMOTE_ADDR="127.0.0.1").wsgi_request

        self.assertEqual(get_author_ip(request), "127.0.0.1")

    def test_post_string_representation(self):
        self.assertEqual(str(self.post1), "Post 1")


class IsOwnerOrReadOnlyTests(TestCase):
    def setUp(self):
        self.permission = IsOwnerOrReadOnly()
        self.user = Users.objects.create_user(
            username="permissionuser",
            email="permission@example.com",
            password="permission123",
        )
        self.post = Posts.objects.create(
            title="Permission Post",
            content="Permission Content",
            username=self.user,
            author_ip="127.0.0.1",
        )

    def test_safe_method_is_allowed(self):
        request = self.client.get("/posts/").wsgi_request

        self.assertTrue(
            self.permission.has_object_permission(request, view=None, obj=self.post)
        )

    def test_unsafe_method_without_authenticated_user_is_denied(self):
        request = self.client.patch(f"/posts/{self.post.id}/", {}).wsgi_request

        self.assertFalse(
            self.permission.has_object_permission(request, view=None, obj=self.post)
        )
