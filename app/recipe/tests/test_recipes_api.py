from email.mime import multipart
import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


default_payload = {
        "title": "Costillas con tomate",
        "time_minutes": 40,
        "price": 4.00
    }

# /api/recipe/recipes
RECIPES_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])

# /api/recipe/recipes/1
def detail_url(recipe_id: int) -> str:
    """Return recipe detail URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])

def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = default_payload.copy()
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, name="sweet"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="tarracon"):
    """Create and return a sample tag"""
    return Ingredient.objects.create(user=user, name=name)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
    
    def test_unauthenticated_access_fails(self):
        """Test that Recipe Endpoint requires authentication"""
        res = self.client.get(RECIPES_URL)

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

        res = self.client.get(RECIPES_URL)

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

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by("-title")
        recipe_serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(recipes))
        self.assertEqual(recipe_serializer.data, res.data)
    
    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)
    
    def test_create_simple_recipe(self):
        """Test creating recipe without tags nor ingredients"""
        res = self.client.post(RECIPES_URL, default_payload)
        new_recipe = Recipe.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in default_payload.keys():
            self.assertEqual(default_payload[key], getattr(new_recipe, key))
    
    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags, no ingredients"""
        payload = default_payload.copy()
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Meaty")
        payload["tags"] = [tag1.id, tag2.id]
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tags), len(payload["tags"]))
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
    
    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients, no tags"""
        payload = default_payload.copy()
        ingredient1 = sample_ingredient(user=self.user, name="Tomato")
        ingredient2 = sample_ingredient(user=self.user, name="Chocolate")
        payload["ingredients"] = [ingredient1.id, ingredient2.id]
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ingredients), len(payload["ingredients"]))
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
    
    def test_partial_update_recipe(self):
        """Test updating a recipe with a PATCH method"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="Curry")

        payload = {"title": "Chicken tikka", "tags": [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)
    
    def test_full_update_recipe(self):
        """Test updating a recipe with a PUT method"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            "title": "Spaghetti carbonara",
            "time_minutes": 25,
            "price": 5.
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        for field in payload.keys():
            self.assertEqual(getattr(recipe, field), payload[field])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="monteros@gmail.com",
            password="TestPass"
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)
    
    def tearDown(self):
        """Cleans up after tests been executed by removing created image"""
        self.recipe.image.delete()
    
    def test_succesful_image_upload(self):
        """Test that image can be uploaded to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format="JPEG")
            # need to set pointer back to beginning of file
            ntf.seek(0)
            # format multipart needed to add data to the request
            res = self.client.post(url, {"image": ntf}, format="multipart")
        
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
    
    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {"image": "not an image!"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



    
