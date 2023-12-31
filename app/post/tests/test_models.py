"""
Tests for the models in post app.
"""

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.test import TestCase

from post.models import Category, Author, Post, Section, Tag, Comment


def create_category(user, **params):
    """Create and return a sample category."""

    defaults = {
        'name': 'Sample Category'
    }
    defaults.update(**params)

    return Category.objects.create(user=user, **defaults)


def create_post(user, **params):
    """Create and return a sample post."""

    defaults = {
        'title': 'Sample Post Title',
        'excerpt': 'Sample post excerpt.',
        'time_read': 3
    }
    defaults.update(**params)

    return Post.objects.create(user=user, **defaults)


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

    def test_create_author_success(self):
        """Test creating an author successfully."""

        payload = {'name': 'Author N. Name'}
        author = Author.objects.create(user=self.user, **payload)

        self.assertTrue(Author.objects.filter(name=payload['name']).exists())
        self.assertEqual(str(author), payload['name'])
        self.assertEqual(author.slug, slugify(payload['name']))


class PostModelTests(TestCase):
    """Tests for post model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test_pass_123'
        )
        self.category = create_category(self.user)
        self.author = Author.objects.create(user=self.user, name='Author Name')

    def test_create_post_success(self):
        """Test creating a post successfully."""

        payload = {
            'title': 'Sample Post Title',
            'excerpt': 'Sample post excerpt.',
            'category': self.category,
            'author': self.author,
            'time_read': 5
            }
        post = Post.objects.create(user=self.user, **payload)

        self.assertTrue(Post.objects.filter(title=payload['title']).exists())
        self.assertEqual(str(post), payload['title'])
        self.assertEqual(post.slug, slugify(payload['title']))
        for k, v in payload.items():
            self.assertEqual(getattr(post, k), v)

    def test_create_section_success(self):
        """Test creating a section of post."""

        post = create_post(
            user=self.user,
            category=self.category,
            author=self.author
        )

        s1 = Section.objects.create(
            user=self.user,
            post=post,
            sub_title='Section 1',
            content='Some post text section.'
        )
        s2 = Section.objects.create(
            user=self.user,
            post=post,
            sub_title='Section 2',
            content='Another post text section.'
        )

        self.assertEqual(post.sections.all().count(), 2)
        self.assertEqual(s1.ordering, 1)
        self.assertEqual(str(s1), '1. Section 1')
        self.assertEqual(s2.ordering, 2)
        self.assertEqual(str(s2), '2. Section 2')

    def test_create_tag_successful(self):
        """Test creating a tag successfully."""

        payload = {'name': 'SampleTag'}
        tag = Tag.objects.create(user=self.user, **payload)

        self.assertTrue(Tag.objects.filter(name=payload['name']).exists())
        self.assertEqual(str(tag), tag.name)

    def test_assign_tag_to_post(self):
        """Test assigning a tag to a post."""

        post = create_post(
            self.user,
            category=self.category,
            author=self.author
        )
        payload = {'name': 'SampleTag'}
        tag = Tag.objects.create(user=self.user, **payload)
        post.tags.add(tag)

        self.assertEqual(post.tags.all().count(), 1)

    def test_create_comment_success(self):
        """Test creating a comment successfully."""

        post = create_post(
            self.user,
            category=self.category,
            author=self.author
        )
        payload = {
            'name': 'John',
            'message': 'Some comment message.',
            'is_visible': True
        }

        comment = Comment.objects.create(user=self.user, post=post, **payload)

        post.refresh_from_db()
        self.assertEqual(post.comments.count(), 1)
        for k, v in payload.items():
            self.assertEqual(getattr(comment, k), v)
