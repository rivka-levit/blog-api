"""
Tags for Tag APIs.
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from post.models import Post, Tag

TAGS_URL = reverse('tag-list')


def detail_url(tag_id):
    """Create and return the url for a detail page."""

    return reverse('tag-detail', args=[tag_id])


def create_post(user, **params):
    """Create and return a sample post object."""

    defaults = {
        'title': 'Sample Post Title',
        'excerpt': 'Sample post excerpt.',
        'time_read': 5
    }
    defaults.update(**params)

    return Post.objects.create(user=user, **defaults)


def create_tag(user, **params):
    """Create and return a sample tag object."""

    defaults = {'name': 'SampleTag'}
    defaults.update(**params)

    return Tag.objects.create(user=user, **defaults)


class PublicTagTest(TestCase):
    """Tests for unauthorized requests."""

    def setUp(self):
        self.client = APIClient()

    def test_not_authenticated_fails(self):
        """Test access forbidden for not authenticated user."""

        r = self.client.get(TAGS_URL)

        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagTests(TestCase):
    """Tests for authenticated users requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test_tags@example.com',
            password='test_pass_123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tag_list_successful(self):
        """Test retrieving the list of posts successfully."""

        create_tag(self.user)
        create_tag(self.user, name='SecondTag')

        r = self.client.get(TAGS_URL)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 2)

    def test_create_tag_assign_user_success(self):
        """Test creating a tag and assigning it to the current user."""

        payload = {'name': 'AwsomeTag'}

        r = self.client.post(TAGS_URL, payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['name'], payload['name'])

    def test_retrieve_single_tag(self):
        """Test retrieving one particular tag."""

        tag = create_tag(self.user)
        url = detail_url(tag.id)

        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['name'], tag.name)

    def test_update_tag_success(self):
        """Test updating a tag successfully."""

        tag = create_tag(self.user)
        url = detail_url(tag.id)
        payload = {'name': 'AnotherTagName'}

        r = self.client.patch(url, payload)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag_success(self):
        """Test removing a tag successfully."""

        tag = create_tag(self.user)
        url = detail_url(tag.id)

        r = self.client.delete(url)

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
