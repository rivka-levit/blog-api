"""
Tests for the models in post app.
"""

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.test import TestCase

from post.models import Category


def create_category(user, **params):
    """Create and return a sample category."""

    defaults = {
        'name': 'Sample Category'
    }
    defaults.update(**params)

    return Category.objects.create(user=user, **defaults)


class ModelTests(TestCase):
    """Tests for models"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test_pass_123'
        )

    def test_category_create(self):
        """Test creating a category object."""

        payload = {'name': 'First Test Category'}

        category = create_category(self.user, **payload)

        self.assertTrue(Category.objects.filter(name=payload['name']).exists())
        self.assertEqual(str(category), payload['name'])
        self.assertEqual(category.slug, slugify(payload['name']))
        self.assertEqual(category.ordering, 1)

    def test_create_category_duplicated_slug_raise_error(self):
        """Test raising an error if the slug is duplicated."""

        create_category(self.user, name='One Unique Name')

        with self.assertRaises(ValidationError):
            create_category(self.user, name='One Unique Name')

    def test_create_category_duplicated_ordering_raise_error(self):
        """Test raising an error if the ordering number is duplicated."""

        create_category(self.user, ordering=5)

        with self.assertRaises(ValidationError):
            create_category(self.user, name='Another Name', ordering=5)
