from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email="test@montero.es", password="test1234"):
  """Create a sample user"""
  return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'juan@montero.com'
        password = 'tesTinghaha123'
        user = get_user_model().objects.create_user(
          email=email,
          password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """Test that the domain part of a user email is normalised"""
        email = 'test@MONTERO.Com'
        user = get_user_model().objects.create_user(email, 'test124')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test124')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
          'test@montero.es',
          'test124'
        )
        # is_superuser attribute defined by PermissionsMixin
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_tag_str(self):
      """Test the tag string representation"""
      tag = models.Tag.objects.create(
        user=sample_user(),
        name='Vegan'
      )

      self.assertEqual(str(tag), tag.name)
    
    def test_ingredients_str(self):
      """Test the ingredient string repr."""
      ingredient = models.Ingredient.objects.create(
        user=sample_user(),
        name="Onions"
      )

      self.assertEqual(str(ingredient), ingredient.name)
