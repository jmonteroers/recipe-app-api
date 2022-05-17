from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

std_payload = {
    "email": "test@monteros.es",
    "password": "testpass",
    "name": "Test random name",
}


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API with unauthenticated requests, e.g. signing up"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        res = self.client.post(CREATE_USER_URL, std_payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # checking that user has actually been created properly, and does not
        # return the password
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(std_payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test that creating a user that already exists fails"""
        create_user(**std_payload)

        res = self.client.post(CREATE_USER_URL, std_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that a password must be longer than 5 characters"""
        payload = {**std_payload, "password": 123}

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        create_user(**std_payload)
        res = self.client.post(TOKEN_URL, std_payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email="test@londonappdev.com", password="testpass")
        payload = {"email": "test@londonappdev.com", "password": "wrong"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user not contained in payload"""
        payload = std_payload.copy()
        del payload["email"]
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {"email": "one", "password": ""})
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorised(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that request authentication"""

    def setUp(self):
        """Whichever request we do, will be authenticated for self.user"""
        self.user = create_user(**std_payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"name": self.user.name, "email": self.user.email})

    def test_post_me_not_allowed(self):
        """Test that POST request not allowed on the ME url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile_success(self):
        """Test updating the user profile for authenticated url"""
        new_payload = {"name": "new name", "password": "newpassword123"}

        res = self.client.patch(ME_URL, new_payload)

        # update user with latest value from DB
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, new_payload["name"])
        self.assertTrue(self.user.check_password(new_payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
