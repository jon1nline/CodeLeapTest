# Create your tests here.
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

Users = get_user_model()


class UserLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = "/users/login/"

        self.user = Users.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )

    def test_login_success(self):
        data = {"username": "testuser", "password": "testpassword123"}

        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)

        self.assertIn("access", response_data)
        self.assertIn("refresh", response_data)

        self.assertTrue(response_data["access"])
        self.assertTrue(response_data["refresh"])

    def test_login_wrong_password(self):
        data = {"username": "testuser", "password": "wrongpassword"}

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "incorrect username or password")

    def test_login_nonexistent_user(self):
        data = {"username": "nonexistent", "password": "anypassword"}

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "incorrect username or password")

    def test_login_missing_fields(self):
        data = {"password": "testpassword123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"username": "testuser"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/users/register/"

    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Users.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):
        Users.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="password123",
        )

        data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "newpassword123",
        }

        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        data = {"email": "test@example.com", "password": "password123"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"username": "testuser", "password": "password123"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"username": "testuser", "email": "test@example.com"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
