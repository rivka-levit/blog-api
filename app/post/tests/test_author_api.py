"""
Tests for Author APIs.
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from post.models import Author

AUTHORS_URL = reverse('author-list')


def detail_url(author_slug):
    """Create and return the url for a detail page."""

    return reverse('author-detail', args=[author_slug])


def create_author(user, **params):
    """Create and return an Author object."""

    defaults = {
        'name': 'John K. Dow'
    }
    defaults.update(**params)

    return Author.objects.create(user=user, **defaults)


class PublicAuthorTest(TestCase):
    """Tests for unauthorized requests."""

    def setUp(self):
        self.client = APIClient()

    def test_not_authenticated_fails(self):
        """Test access forbidden for not authenticated user."""

        r = self.client.get(AUTHORS_URL)

        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAuthorTest(TestCase):
    """Tests for authenticated users requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test_author@example.com',
            password='test_pass_123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_author_list_successful(self):
        """Test retrieving the list of categories successfully."""

        create_author(self.user, name='Author 1')
        create_author(self.user, name='Author 2')

        r = self.client.get(AUTHORS_URL)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 2)

    def test_create_author_assign_user_success(self):
        """Test creating an author and assigning it to the current user."""

        payload = {
            'name': 'Katarina Santi'
        }

        r = self.client.post(AUTHORS_URL, payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['name'], payload['name'])

        category = Author.objects.get(name=payload['name'])
        self.assertEqual(category.user, self.user)

    def test_retrieve_single_author(self):
        """Test retrieving one particular author."""

        author = create_author(self.user)
        url = detail_url(author.slug)

        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['name'], author.name)

    def test_update_author_success(self):
        """Test updating an author successfully."""

        author = create_author(self.user)

        payload = {
            'name': 'John Kerstin Dow'
        }

        url = detail_url(author.slug)
        r = self.client.patch(url, payload)

        self.assertEqual(r.status_code, status.HTTP_200_OK)

        author.refresh_from_db()
        self.assertEqual(author.name, payload['name'])

    def test_delete_author_success(self):
        """Test removing an author successfully."""

        author = create_author(self.user)
        auth_id = author.id

        url = detail_url(author.slug)
        r = self.client.delete(url)

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(id=auth_id).exists())
