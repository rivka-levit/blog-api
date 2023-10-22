"""Tests for Category APIs."""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from post.models import Category

CATEGORIES_URL = reverse('category-list')


def detail_url(category_slug):
    """Create and return the url for a detail page."""

    return reverse('category-detail', args=[category_slug])


def create_category(user, **params):
    """Create and return a Category object."""

    defaults = {
        'name': 'Sample Category'
    }
    defaults.update(**params)

    return Category.objects.create(user=user, **defaults)


class PublicCategoryTest(TestCase):
    """Tests for unauthorized requests."""

    def setUp(self):
        self.client = APIClient()

    def test_not_authenticated_fails(self):
        """Test access forbidden for not authenticated user."""

        r = self.client.get(CATEGORIES_URL)

        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryTest(TestCase):
    """Tests for authenticated users requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test_category@example.com',
            password='test_pass_123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_category_list_successful(self):
        """Test retrieving the list of categories successfully."""
        create_category(self.user, name='cat 1')
        create_category(self.user, name='cat 2')

        r = self.client.get(CATEGORIES_URL)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 2)

    def test_create_category_assign_user_success(self):
        """Test creating a category and assigning it to the current user."""

        payload = {
            'name': 'Monitors'
        }

        r = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['name'], payload['name'])
        self.assertEqual(r.data['ordering'], 1)

        category = Category.objects.get(name=payload['name'])
        self.assertEqual(category.user, self.user)

    def test_create_category_with_custom_slug(self):
        """Test creating a category with custom slug"""

        payload = {
            'name': 'Travelling',
            'slug': 'my-favorite-travellings'
        }

        r = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['slug'], payload['slug'])

    def test_create_category_with_custom_ordering(self):
        """Test creating a category with custom ordering number"""

        payload = {
            'name': 'Shoes',
            'ordering': 5
        }

        r = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['ordering'], payload['ordering'])

    def test_retrieve_single_category(self):
        """Test retrieving one particular category."""

        category = create_category(self.user)
        url = detail_url(category.slug)

        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['name'], category.name)

    def test_update_category_success(self):
        """Test updating a category successfully."""

        category = create_category(self.user)

        payload = {
            'name': 'New Name',
            'ordering': 3
        }

        url = detail_url(category.slug)
        r = self.client.patch(url, payload)

        self.assertEqual(r.status_code, status.HTTP_200_OK)

        category.refresh_from_db()
        for attr, value in payload.items():
            self.assertEqual(getattr(category, attr), value)

    def test_delete_category_success(self):
        """Test removing a category successfully."""

        category = create_category(self.user)
        cat_id = category.id

        url = detail_url(category.slug)
        r = self.client.delete(url)

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=cat_id).exists())
