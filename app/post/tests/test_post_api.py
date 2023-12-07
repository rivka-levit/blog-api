"""
Tests for Post APIs.
"""
import tempfile
import os

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from PIL import Image

from post.models import Post, Author, Category, Section, Tag, Comment

POSTS_URL = reverse('post-list')


def detail_url(post_slug):
    """Create and return the url for a detail page."""

    return reverse('post-detail', args=[post_slug])


def upload_image_url(post_slug):
    """Create and return the url for an uploading an image."""

    return reverse('post-upload-image', args=[post_slug])


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
        self.author = Author.objects.create(user=self.user, name='John Dow')
        self.category = Category.objects.create(
            user=self.user,
            name='Sample Category'
        )

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

    def test_create_post_with_category_author(self):
        """Test creating a post and assigning existing category and author."""

        payload = {
            'title': 'My Awsome Post',
            'excerpt': 'Cool excerpt of my post.',
            'time_read': 7,
            'category': {'name': self.category.name, 'slug': self.category.slug},
            'author': {'name': self.author.name, 'slug': self.author.slug}
        }

        r = self.client.post(POSTS_URL, payload, format='json')

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(title=payload['title'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.category, self.category)

    def test_update_post_with_category_author(self):
        """Test updating the category and the author in a post."""

        post = create_post(self.user)

        payload = {
            'title': 'New Title',
            'category': {
                'name': self.category.name,
                'slug': self.category.slug
            },
            'author': {
                'name': self.author.name,
                'slug': self.author.slug
            }
        }

        url = detail_url(post.slug)
        r = self.client.patch(url, payload, format='json')

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.author, self.author)

    def test_create_post_with_sections(self):
        """Test creating a post with text sections."""

        payload = {
            'title': 'My Awsome Post',
            'excerpt': 'Cool excerpt of my post.',
            'time_read': 7,
            'category': {'name': self.category.name, 'slug': self.category.slug},
            'author': {'name': self.author.name, 'slug': self.author.slug},
            'sections': [
                {
                    'sub_title': 'First Text Section',
                    'content': 'Lorem ipsum dolor sit amet, consectetur '
                               'adipiscing elit, sed do eiusmod tempor '
                               'incididunt ut labore et dolore magna aliqua. '
                               'Ut enim ad minim veniam, quis nostrud '
                               'id est laborum.'
                },
                {
                    'sub_title': 'Second Text Section',
                    'content': 'Lorem ipsum dolor sit amet, consectetur '
                               'adipiscing elit, sed do eiusmod tempor '
                               'incididunt ut labore et dolore magna aliqua. '
                               'Ut enim ad minim veniam, quis nostrud '
                               'id est laborum.'
                },
                {
                    'sub_title': 'Third Text Section',
                    'content': 'Lorem ipsum dolor sit amet, consectetur '
                               'adipiscing elit, sed do eiusmod tempor '
                               'incididunt ut labore et dolore magna aliqua. '
                               'Ut enim ad minim veniam, quis nostrud '
                               'id est laborum.'
                }
            ]
        }

        r = self.client.post(POSTS_URL, payload, format='json')

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(user=self.user, title=payload['title'])
        self.assertEqual(len(r.data['sections']), post.sections.count())
        post_sections = post.sections.all()
        for section in payload['sections']:
            self.assertTrue(
                post_sections.filter(sub_title=section['sub_title']).exists()
            )

    def test_update_post_sections(self):
        """Test updating the sections in a post."""

        post = create_post(self.user)
        Section.objects.create(
            user=self.user,
            post=post,
            sub_title='Sample Section',
            content='Lorem ipsum dolor sit amet, consectetur '
                    'adipiscing elit, sed do eiusmod tempor '
                    'incididunt ut labore et dolore magna aliqua. '
                    'Ut enim ad minim veniam, quis nostrud '
                    'id est laborum.'
        )

        payload = {'sections': [
            {
                'sub_title': 'Second Text Section',
                'content': 'Lorem ipsum dolor sit amet, consectetur '
                           'adipiscing elit, sed do eiusmod tempor '
                           'incididunt ut labore et dolore magna aliqua. '
                           'Ut enim ad minim veniam, quis nostrud '
                           'id est laborum.',
                'ordering': 2
            },
            {
                'sub_title': 'First Text Section',
                'content': 'Lorem ipsum dolor sit amet, consectetur '
                           'adipiscing elit, sed do eiusmod tempor '
                           'incididunt ut labore et dolore magna aliqua. '
                           'Ut enim ad minim veniam, quis nostrud '
                           'id est laborum.',
                'ordering': 1
            }
        ]}

        url = detail_url(post.slug)
        r = self.client.patch(url, payload, format='json')

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data['sections']), 2)

    def test_create_post_with_tags(self):
        """Test creating a post with tags."""

        payload = {
            'title': 'My Awsome Post',
            'excerpt': 'Cool excerpt of my post.',
            'time_read': 3,
            'tags': [
                {'name': 'tag1'},
                {'name': 'tag2'}
            ]
        }

        r = self.client.post(POSTS_URL, payload, format='json')

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(title=payload['title'])
        self.assertEqual(post.tags.count(), len(payload['tags']))

    def test_update_post_with_tags(self):
        """Test updating a post with tags."""

        post = create_post(self.user)
        tag = Tag.objects.create(user=self.user, name='OldTag')
        post.tags.add(tag)

        payload = {
            'tags': [
                {'name': 'tag1'},
                {'name': 'tag2'}
            ]
        }
        url = detail_url(post.slug)

        r = self.client.patch(url, payload, format='json')

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data['tags']), 2)
        post.refresh_from_db()
        self.assertFalse(Post.objects.filter(tags__in=[tag]).exists())

    def test_update_single_post_section(self):
        """Test updating single section of a post."""

        post = create_post(self.user)
        section = Section.objects.create(
            user=self.user,
            post=post,
            sub_title='Some Subtitle',
            content='Some content.'
        )
        payload = {'sub_title': 'New Subtitle'}
        url = reverse('post-update-section',
                      args=[post.slug, section.ordering])

        r = self.client.patch(url, payload)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        section.refresh_from_db()
        self.assertEqual(section.sub_title, payload['sub_title'])

    def test_delete_single_post_section(self):
        """Test removing a single section of a post."""

        post = create_post(self.user)
        section = Section.objects.create(
            user=self.user,
            post=post,
            sub_title='Some Subtitle',
            content='Some content.'
        )
        url = reverse('post-delete-section',
                      args=[post.slug, section.ordering])

        r = self.client.delete(url)

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        post.refresh_from_db()
        self.assertEqual(post.sections.all().count(), 0)

    def test_retrieve_post_with_comments(self):
        """Test retrieving a post with the comments assigned."""

        payload = {
            'category': self.category,
            'author': self.author
        }
        post = create_post(self.user, **payload)
        Comment.objects.create(user=self.user, post=post,
                               message='some msg', is_visible=True)
        Comment.objects.create(user=self.user, post=post,
                               message='another msg', is_visible=True)
        post.refresh_from_db()

        url = detail_url(post.slug)
        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data['comments']), 2)

    def test_retrieve_only_visible_comments_in_post(self):
        """Test retrieving only the comments that are visible in post."""

        post = create_post(self.user)
        Comment.objects.create(user=self.user, post=post,
                               message='some msg')
        Comment.objects.create(user=self.user, post=post,
                               message='another msg', is_visible=True)

        url = detail_url(post.slug)
        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data['comments']), 1)

    def test_filter_posts_by_author(self):
        """Test filtering posts by author."""

        author2 = Author.objects.create(user=self.user, name='Sarah Falcon')

        create_post(self.user, author=self.author)
        post2 = create_post(self.user, title='another post', author=author2)

        params = {"author": author2.slug}

        r = self.client.get(POSTS_URL, params)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['slug'], post2.slug)

    def test_filter_posts_by_category(self):
        """Test filtering posts by category."""

        category = Category.objects.create(user=self.user, name='Category 2')

        post = create_post(self.user, category=category)
        create_post(self.user, title='another post', category=self.category)

        params = {"category": category.slug}

        r = self.client.get(POSTS_URL, params)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['slug'], post.slug)

    def test_filter_posts_by_tags(self):
        """Tests filtering posts by tags."""

        tag1 = Tag.objects.create(user=self.user, name='Tag1')
        tag2 = Tag.objects.create(user=self.user, name='Tag2')
        post1 = create_post(self.user, title='post 1')
        post1.tags.add(tag1)
        post2 = create_post(self.user, title='post 2')
        post2.tags.add(tag2)
        create_post(self.user)

        params = {"tags": f'{tag1.id},{tag2.id}'}

        r = self.client.get(POSTS_URL, params)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 2)


class UploadImageTests(TestCase):
    """Tests for uploading image."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test_image@example.com',
            password='test_pass_123'
        )
        self.client.force_authenticate(user=self.user)
        self.post = create_post(self.user)

    def tearDown(self):
        self.post.image.delete()

    def test_upload_image_to_post(self):
        """Test uploading image to a post successfully."""

        url = upload_image_url(self.post.slug)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, 'JPEG')
            image_file.seek(0)
            payload = {'image': image_file}

            r = self.client.post(url, payload, format='multipart')

        self.post.refresh_from_db()

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(os.path.exists(self.post.image.path))
