from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        "title": "Costillas con tomate",
        "time_minutes": 40,
        "price": 4.00
    }
    defaults.update(params)
    return Recipe(user=user, **defaults)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
    
    def test_unauthenticated_access_fails(self):
        """Test that Recipe Endpoint requires authentication"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="monteros@gmail.com",
            password="TestPass"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_succesful_recipe_list(self):
        """Test that authenticated user gets a list of their recipes"""
        sample_recipe(self.user)
        sample_recipe(self.user, title="Roasted fish")

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-title")
        recipe_serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(recipes))
        self.assertEqual(recipe_serializer.data, res.data)
    
    def test_listed_recipes_limited_auth_user(self):
        """Test that authenticated user only gets their own recipes"""
        user2 = get_user_model().objects.create_user(
            email="test@yopmail.com",
            password="1234"
        )
        sample_recipe(self.user)
        sample_recipe(user2, title="Roasted fish")

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by("-title")
        recipe_serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(recipes))
        self.assertEqual(recipe_serializer.data, res.data)





