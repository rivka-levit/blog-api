"""
Tests for Post APIs.
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from post.models import Post

POSTS_URL = reverse('post-list')


def detail_url(post_slug):
    """Create and return the url for a detail page."""

    return reverse('post-detail', args=[post_slug])


def create_post(user, **params):
    """Create and return a sample post object."""

    defaults = {
        'title': 'Sample Post Title',
        'excerpt': 'Sample post excerpt.',
        'time_read': 5
    }
    defaults.update(**params)

    return Post.objects.create(user=user, **defaults)


class PublicPostTest(TestCase):
    """Tests for unauthorized requests."""

    def setUp(self):
        self.client = APIClient()

    def test_not_authenticated_fails(self):
        """Test access forbidden for not authenticated user."""

        r = self.client.get(POSTS_URL)

        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePostTest(TestCase):
    """Tests for authenticated users requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test_post@example.com',
            password='test_pass_123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_post_list_successful(self):
        """Test retrieving the list of posts successfully."""

        create_post(self.user, title='First Post')
        create_post(self.user, title='Second Post')

        r = self.client.get(POSTS_URL)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 2)

    def test_create_post_assign_user_success(self):
        """Test creating a post and assigning it to the current user."""

        payload = {
            'title': 'My Awsome Post',
            'excerpt': 'Cool excerpt of my post.',
            'time_read': 7
        }

        r = self.client.post(POSTS_URL, payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        post = Post.objects.get(title=payload['title'])
        self.assertEqual(post.user, self.user)

        for attr in payload:
            self.assertEqual(r.data[attr], payload[attr])

    def test_retrieve_single_post(self):
        """Test retrieving one particular post."""

        post = create_post(self.user)
        url = detail_url(post.slug)

        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['title'], post.title)

    def test_update_post_success(self):
        """Test updating a post successfully."""

        post = create_post(self.user)

        payload = {
            'title': 'New Post Title',
            'excerpt': 'New excerpt for the post.',
        }

        url = detail_url(post.slug)
        r = self.client.patch(url, payload)

        self.assertEqual(r.status_code, status.HTTP_200_OK)

        post.refresh_from_db()
        for attr in payload:
            self.assertEqual(getattr(post, attr), payload[attr])

    def test_delete_post_success(self):
        """Test removing a post successfully."""

        post = create_post(self.user)
        post_id = post.id

        url = detail_url(post.slug)
        r = self.client.delete(url)

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post_id).exists())
