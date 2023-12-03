"""
Tests for Comments APIs.
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from post.models import Post, Comment

COMMENTS_URL = reverse('comment-list')


def detail_url(comment_id):
    """Create and return the url for a detail page."""

    return reverse('comment-detail', args=[comment_id])


def create_post(user, **params):
    """Create and return a sample post object."""

    defaults = {
        'title': 'Some Particular Post',
        'excerpt': 'Little post excerpt.',
        'time_read': 3
    }
    defaults.update(**params)

    return Post.objects.create(user=user, **defaults)


def create_comment(user, post, **params):
    """Create and return a sample tag object."""

    defaults = {
        'name': 'John',
        'message': 'Some sample message.'
    }
    defaults.update(**params)

    return Comment.objects.create(user=user, post=post, **defaults)


class CommentsTests(TestCase):
    """Tests for unauthorized requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test_comments@example.com',
            password='test_pass_123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.post = create_post(self.user)

    def test_retrieve_comments_list_success(self):
        """Test retrieving list of comments successfully."""

        cmt1 = create_comment(self.user, self.post)
        cmt2 = create_comment(self.user, self.post, name='Jack')
        self.post.refresh_from_db()

        r = self.client.get(COMMENTS_URL)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 2)
        self.assertEqual(r.data[1]['name'], cmt2.name)
        for comment in r.data:
            self.assertEqual(comment['post_slug'], self.post.slug)

    def test_create_comment_success(self):
        """Test creating a comment successfully."""

        payload = {
            'post_slug': self.post.slug,
            'name': 'Mike',
            'message': 'Some message.'
        }

        r = self.client.post(COMMENTS_URL, payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(r.data[k], v)

    def test_retrieve_single_comment(self):
        """Test retrieving a single comment."""

        cmt = create_comment(self.user, self.post)
        url = detail_url(cmt.id)

        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['name'], cmt.name)
        self.assertEqual(r.data['message'], cmt.message)

    def test_update_comment_success(self):
        """Test partial updating of a comment."""

        cmt = create_comment(self.user, self.post)
        url = detail_url(cmt.id)
        payload = {'name': 'New Name'}

        r = self.client.patch(url, payload)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        cmt.refresh_from_db()
        self.assertEqual(cmt.name, payload['name'])

    def test_full_update_comment_success(self):
        """Test full updating of a comment."""

        cmt = create_comment(self.user, self.post, name='Anna')
        url = detail_url(cmt.id)
        post_2 = create_post(self.user, title='another title', time_read=7)
        payload = {
            'post_slug': post_2.slug,
            'name': 'New Name',
            'message': 'Changed message.'
        }

        r = self.client.put(url, payload)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        cmt.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(r.data[k], v)

    def test_delete_comment(self):
        """Test deleting a comment successfully."""

        cmt = create_comment(self.user, self.post)
        url = detail_url(cmt.id)

        r = self.client.delete(url)

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
