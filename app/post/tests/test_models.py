"""
Tests for the models in post app.
"""

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.test import TestCase

from post.models import Category


class ModelTests(TestCase):
    """Tests for models"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test_pass_123'
        )

    def test_category_create(self):
        """Test creating a category object."""

        payload = {'name': 'Sample Category', 'user': self.user}

        category = Category.objects.create(**payload)

        self.assertTrue(Category.objects.filter(name=payload['name']).exists())
        self.assertEqual(str(category), payload['name'])
        self.assertEqual(category.slug, slugify(payload['name']))
        self.assertEqual(category.ordering, 1)

